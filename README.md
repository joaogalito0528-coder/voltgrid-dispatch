# VoltGrid Dispatch - Orquestração de Recarga de Frotas Elétricas Concorrentes

## Integrantes
Caio Rohr Vargas
João Eduardo Herculano Galito
João Lucas Rodrigues
Pedro Henrique de Paula Caetano

## Tema e Domínio de Negócio
- **Tema:** 4. VoltGrid Dispatch (Orquestração de Recarga de Frotas Elétricas Concorrentes)
- **Disciplina:** Programação Distribuída e Paralela (Faculdade Multivix - 2026/2)
- **Descrição:** O sistema gerencia solicitações em tempo real de eletropostos metropolitanos, aplicando mensageria assíncrona, relógios vetoriais para rastreamento de causalidade, exclusão mútua distribuída para proteção de sobrecarga nas subestações e eleição de líder baseada no algoritmo Bully.

## Estrutura do Projeto
O repositório está organizado em módulos independentes que compõem a arquitetura distribuída:

```text
voltgrid-dispatch/
├── proto/
│   └── voltgrid.proto
├── gateway/
│   ├── __init__.py
│   └── gateway_server.py
├── worker/
│   ├── __init__.py
│   ├── vector_clock.py
│   ├── bully_election.py
│   └── worker_node.py
├── persistence/
│   ├── __init__.py
│   └── storage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

Arquitetura e Decisões TécnicasO projeto fundamenta-se no padrão "A Metrópole Resiliente" e atende rigorosamente aos seguintes requisitos técnicos:
1. Camada de Ingress (R1): Utiliza gRPC com Protocol Buffers (voltgrid.proto) para garantir comunicação binária de alta performance e processamento assíncrono não bloqueante no ponto de entrada.
2. Buffer Distribuído / Mensageria (R2): Integração com RabbitMQ para desacoplar a interface cliente do processamento pesado, garantindo durabilidade das mensagens (delivery_mode=2).
3. Workers Replicados (R3 & R6): Três nós trabalhadores independentes executam sob o padrão Competing Consumers. Em caso de falhas, o sistema utiliza o mecanismo de acknowledgment (basic_ack / basic_nack com requeue=True) para evitar a perda de dados.
4. Sincronização Lógica (R4): Implementação de Relógios Vetoriais para rastrear a causalidade exata das solicitações de recarga de frota sem dependência de relógio físico centralizado.
5. Eleição de Líder (R5): Execução do Algoritmo do Valentão (Bully) para eleger dinamicamente o nó coordenador responsável por gerenciar as consolidações do cluster.
6. Controle de Cota e Persistência: Implementação de exclusão mútua distribuída para gerenciar os limites de potência das subestações, com armazenamento primário e réplicas de estado consistentes.

Guia de Execução Local
Certifique-se de ter o Docker e o Docker Compose instalados na sua máquina.

Na raiz do repositório, execute o comando para subir toda a infraestrutura:

Bash
docker-compose up --build
O ambiente iniciará automaticamente o broker RabbitMQ, o Gateway gRPC e os 3 nós trabalhadores concorrentes.

Declaração de Uso de IA
Conforme a política institucional da disciplina, declaramos que a ferramenta de Inteligência Artificial Gemini foi utilizada estritamente como um recurso de apoio técnico e educacional ao longo do desenvolvimento. O papel da IA concentrou-se em auxiliar na resolução de dúvidas conceituais, depuração de erros de sintaxe e código que ocorriam durante a estruturação dos módulos, e suporte na formatação dos arquivos de configuração, sendo todo o código e as decisões arquiteturais revisados, compreendidos e validados inteiramente pela equipe.



