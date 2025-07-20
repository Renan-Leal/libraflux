# Etapa 1: build
FROM python:3.11-slim AS builder

WORKDIR /app

# Instala ferramentas essenciais apenas para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instala dependências em uma pasta separada
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Etapa 2: imagem final
FROM python:3.11-slim AS final

WORKDIR /app

# Copia dependências da etapa anterior
COPY --from=builder /install /usr/local

# Copia somente os arquivos necessários do projeto
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
