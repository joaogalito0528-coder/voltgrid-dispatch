# VoltGrid Dispatch

## Integrantes
Caio Rohr Vargas - 6-2210294
João Eduardo Herculano Galito - Mat. 6-2210315
João Lucas Rodrigues - Mat. 6-2512170
Pedro Henrique de Paula Caetano - Mat. 6-2210256

## Tema e Domínio de Negócio
**VoltGrid Dispatch**: Sistema distribuído voltado para a orquestração inteligente e tolerante a falhas de recarga de frotas de veículos elétricos, utilizando mensageria assíncrona, relógios lógicos e coordenação baseada em eleição de líder.

## Estrutura do Repositório
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
```
# Arquitetura e Decisões Técnicas

O projeto fundamenta-se no padrão "A Metrópole Resiliente" e atende rigorosamente aos seguintes requisitos técnicos:

1- Camada de Ingress (R1): Utiliza gRPC com Protocol Buffers (voltgrid.proto) para garantir comunicação binária de alta performance e processamento assíncrono não bloqueante no ponto de entrada.

2- Buffer Distribuído / Mensageria (R2): Integração com RabbitMQ para desacoplar a interface cliente do processamento pesado, garantindo durabilidade das mensagens (delivery_mode=2).

3- Workers Replicados (R3 & R6): Três nós trabalhadores independentes executam sob o padrão Competing Consumers. Em caso de falhas, o sistema utiliza o mecanismo de acknowledgment (basic_ack / basic_nack com requeue=True) para evitar a perda de dados.

4- Sincronização Lógica (R4): Implementação de Relógios Vetoriais para rastrear a causalidade exata das solicitações de recarga de frota sem dependência de relógio físico centralizado.

5- Eleição de Líder (R5): Execução do Algoritmo do Valentão (Bully) para eleger dinamicamente o nó coordenador responsável por gerenciar as consolidações do cluster.

6- Controle de Cota e Persistência: Implementação de exclusão mútua distribuída para gerenciar os limites de potência das subestações, com armazenamento primário e réplicas de estado consistentes.

## Diagrama de Arquitetura e Fluxo de Mensagens
O diagrama abaixo ilustra a topologia de rede, as portas utilizadas e o fluxo de dados entre os componentes do sistema:
O fluxo do sistema começa no cliente gRPC, que se comunica com o Gateway Server pela porta 50051. Em seguida, o Gateway publica uma mensagem JSON na fila (recharge_queue) do RabbitMQ Broker (utilizando as portas 5672 para a aplicação e 15672 para a interface web). O broker distribui as tarefas de forma justa entre múltiplos workers concorrentes que utilizam relógios vetoriais e o algoritmo Bully. Por fim, os workers processam as requisições e realizam a persistência dos dados de forma replicada através do módulo de armazenamento.

## Guia de Execução Local
Certifique-se de ter o Docker e o Docker Compose instalados na sua máquina.

Na raiz do repositório, execute o comando para subir toda a infraestrutura:
    - docker-compose up --build

## Evidência dos Logs (Console)
Abaixo encontra-se uma amostragem típica do console demonstrando a atualização concorrente dos relógios vetoriais e o funcionamento do algoritmo de eleição do Bully entre os workers:

[2026-09-10 10:15:00] [INFO] [Worker-1] Conectado ao RabbitMQ na fila 'recharge_queue'.

[2026-09-10 10:15:02] [INFO] [Worker-1] Mensagem recebida. Relógio Vetorial anterior: {'worker-1': 0, 'worker-2': 0}

[2026-09-10 10:15:02] [INFO] [Worker-1] Evento processado causalmente. Novo Relógio Vetorial: {'worker-1': 1, 'worker-2': 0}

[2026-09-10 10:15:05] [WARNING] [Worker-2] Conexão com o líder perdida. Iniciando Algoritmo do Bully...

[2026-09-10 10:15:05] [INFO] [Worker-2] Enviando mensagem ELECTION para nós com IDs superiores.

[2026-09-10 10:15:06] [INFO] [Worker-2] Nenhuma resposta recebida. Declarando-se o novo líder (Coordenador).

## Declaração de Uso de IA
Conforme a política institucional da disciplina, declaramos que a ferramenta de Inteligência Artificial Gemini foi utilizada estritamente como um recurso de apoio técnico e educacional ao longo do desenvolvimento. O papel da IA concentrou-se em auxiliar na resolução de dúvidas conceituais, depuração de erros de sintaxe e código que ocorriam durante a estruturação dos módulos, e suporte na formatação dos arquivos de configuração, sendo todo o código e as decisões arquiteturais revisados, compreendidos e validados inteiramente pela equipe.
