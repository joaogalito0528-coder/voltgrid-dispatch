# Usa uma imagem oficial leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte para o container
COPY . .

# Comando padrão executado ao iniciar o container
CMD ["python", "gateway/gateway_server.py"]
