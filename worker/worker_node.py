# ==============================================================================
# COMPONENTE: Nó Trabalhador Principal (Worker Node)
# Domínio: Processamento Concorrente, Mensageria RabbitMQ e Exclusão Mútua
# ==============================================================================

import pika
import json
import os
import time

from vector_clock import VectorClock
from bully_election import BullyElection
from persistence.storage import ReplicatedStorage

class WorkerNode:
    """
    Representa um nó trabalhador da frota elétrica. Consome solicitações do RabbitMQ,
    sincroniza o estado via relógios vetoriais e gerencia a persistência.
    """
    def __init__(self, node_id="worker-1", total_nodes=3):
        self.node_id = node_id
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        
        # Inicializa componentes auxiliares criados anteriormente
        self.vector_clock = VectorClock(node_id, total_nodes)
        self.storage = ReplicatedStorage()
        
        # Inicializa o mecanismo de eleição do Bully
        active_nodes = [{"id": i+1, "priority": (i+1)*10} for i in range(total_nodes)]
        self.bully = BullyElection(node_id=1, node_priority=30, active_nodes=active_nodes)

    def start_consuming(self):
        """Conecta ao RabbitMQ e começa a consumir a fila de recargas de forma concorrente."""
        print(f"[{self.node_id}] Conectando ao RabbitMQ em {self.rabbitmq_host}...")
        
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        channel = connection.channel()
        
        # Declara a mesma fila durável criada no Gateway
        channel.queue_declare(queue='recharge_queue', durable=True)
        
        # Configura o consumo justo (fair dispatch)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='recharge_queue', on_message_callback=self._process_message)
        
        print(f"[{self.node_id}] Aguardando mensagens de recarga na fila...")
        channel.start_consuming()

    def _process_message(self, ch, method, properties, body):
        """Callback executado cada vez que uma solicitação de recarga chega do buffer."""
        try:
            payload = json.loads(body.decode('utf-8'))
            transaction_id = payload.get("transaction_id")
            
            print(f"\n[{self.node_id}] Processando transação: {transaction_id}")
            
            # Incrementa o relógio vetorial local para o evento de processamento
            current_vc = self.vector_clock.tick()
            print(f"[{self.node_id}] Relógio Vetorial atual: {current_vc}")
            
            # Adiciona o relógio vetorial ao payload de dados
            payload["vector_clock"] = current_vc
            
            # Salva a transação utilizando o componente de persistência
            self.storage.save_transaction(payload)
            
            # Confere o processamento com sucesso ao RabbitMQ (Remove da fila)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[{self.node_id}] Transação {transaction_id} concluída e confirmada (ACK).")
            
        except Exception as e:
            print(f"[{self.node_id}] Erro ao processar mensagem: {e}")
            # Em caso de erro, devolve a mensagem para a fila (requeue)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == "__main__":
    node_id = os.getenv("NODE_ID", "worker-1")
    worker = WorkerNode(node_id=node_id)
    
    # Inicia opcionalmente uma verificação de liderança pelo Bully
    worker.bully.start_election()
    
    # Inicia o consumo das mensagens
    worker.start_consuming()
