# ==============================================================================
# COMPONENTE: Persistência Replicada (Storage)
# Domínio: Armazenamento Confiável de Transações e Estado das Subestações
# ==============================================================================

import json
import os

class ReplicatedStorage:
    """
    Gerencia a persistência local de dados das recargas e simula a replicação
    entre nós para garantir consistência e durabilidade.
    """
    def __init__(self, storage_file="voltgrid_data.json"):
        self.storage_file = storage_file
        self._initialize_storage()

    def _initialize_storage(self):
        """Cria o arquivo de armazenamento local caso ele ainda não exista."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({"transactions": [], "station_quotas": {}}, f, indent=4)

    def save_transaction(self, transaction_data):
        """
        Salva uma transação de recarga processada no armazenamento persistente
        e propaga a atualização para as réplicas.
        """
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Adiciona a nova transação
            data["transactions"].append(transaction_data)
            
            # Salva de volta no arquivo (persistência física em disco/volume Docker)
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            print(f"[Storage] Transação {transaction_data.get('transaction_id')} salva com sucesso.")
            self._replicate_to_peers(transaction_data)
            return True
        except Exception as e:
            print(f"[Storage] Erro ao salvar transação: {e}")
            return False

    def _replicate_to_peers(self, transaction_data):
        """
        Simula a replicação do estado gravado para os demais nós do cluster
        garantindo a redundância dos dados.
        """
        print(f"[Storage] Replicando dados da transação para os nós de backup...")
