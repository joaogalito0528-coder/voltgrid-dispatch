import grpc
from concurrent import futures
import time
import os
import pika
import json
import uuid

import voltgrid_pb2
import voltgrid_pb2_grpc

class VoltGridServicer(voltgrid_pb2_grpc.VoltGridServiceServicer):
    def __init__(self):
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        
    def _publish_to_rabbitmq(self, data):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue='recharge_queue', durable=True)
            
            channel.basic_publish(
                exchange='',
                routing_key='recharge_queue',
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2, # Mensagem persistente
                )
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Erro ao publicar no RabbitMQ: {e}")
            return False

    def RequestRecharge(self, request, context):
        transaction_id = str(uuid.uuid4())
        print(f"[Gateway] Recebida requisição de recarga para o veículo {request.vehicle_id} na estação {request.station_id}")
        
        payload = {
            "transaction_id": transaction_id,
            "station_id": request.station_id,
            "vehicle_id": request.vehicle_id,
            "power_kw": request.power_kw,
            "timestamp": time.time()
        }
        
        success = self._publish_to_rabbitmq(payload)
        
        if success:
            return voltgrid_pb2.RechargeResponse(
                transaction_id=transaction_id,
                status="ACEITO_FILA",
                message="Solicitação encaminhada com sucesso para o buffer de processamento."
            )
        else:
            return voltgrid_pb2.RechargeResponse(
                transaction_id=transaction_id,
                status="ERRO_INTERNO",
                message="Falha ao enfileirar solicitação no broker de mensageria."
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voltgrid_pb2_grpc.add_VoltGridServiceServicer_to_server(VoltGridServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("[Gateway] gRPC Server rodando na porta 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
