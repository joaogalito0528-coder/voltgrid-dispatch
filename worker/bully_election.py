# ==============================================================================
# COMPONENTE: Algoritmo do Valentão (Bully Election)
# Domínio: Eleição Distribuída de Líder (Requisito R5)
# ==============================================================================

import time

class BullyElection:
    """
    Implementa o Algoritmo do Bully para eleger dinamicamente um nó coordenador
    entre os workers da frota em caso de falha ou inicialização.
    """
    def __init__(self, node_id, node_priority, active_nodes):
        self.node_id = node_id                  # ID único do nó atual (ex: 1, 2, 3)
        self.priority = node_priority          # Prioridade/peso do nó (quanto maior, mais "valentão")
        self.active_nodes = active_nodes        # Lista de dicionários com os nós conhecidos na rede
        self.current_coordinator = None         # ID do líder atual eleito
        self.is_leader = False                  # Flag indicando se este nó é o líder

    def start_election(self):
        """
        Inicia o processo de eleição. O nó envia uma mensagem de eleição para 
        todos os nós que possuem prioridade superior à sua.
        """
        print(f"[Bully] Nó {self.node_id} iniciou uma eleição de líder.")
        higher_priority_nodes = [n for n in self.active_nodes if n['priority'] > self.priority]
        
        response_received = False

        # Simula o envio de mensagem de eleição para os nós de maior prioridade
        for node in higher_priority_nodes:
            print(f"[Bully] Nó {self.node_id} enviou ELECTION para o nó {node['id']}")
            # Em um ambiente de rede real, aqui haveria uma chamada RPC ou socket.
            # Se algum nó superior responder, ele assume a eleição.
            has_responded = self._simulate_peer_response(node['id'])
            if has_responded:
                response_received = True

        # Se nenhum nó de maior prioridade respondeu, este nó assume a liderança
        if not response_received:
            self.elect_self()

    def _simulate_peer_response(self, peer_id):
        """
        Função auxiliar para simular se um nó superior está ativo na rede.
        No protótipo, podemos ajustar para simular falhas de nós específicos.
        """
        # Exemplo simplificado: assume que nós pares estão ativos e ímpares podem falhar
        return False  

    def elect_self(self):
        """Declara o nó atual como o coordenador/líder do cluster."""
        self.is_leader = True
        self.current_coordinator = self.node_id
        print(f"[Bully] Nenhum nó superior respondeu. Nó {self.node_id} é o novo LÍDER (Coordenador)!")
        self.broadcast_coordinator()

    def broadcast_coordinator(self):
        """Informa a todos os outros nós da rede quem é o novo líder eleito."""
        print(f"[Bully] Nó {self.node_id} anunciando vitória para todos os workers da frota.")
