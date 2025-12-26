FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install LightRAG
RUN pip install --no-cache-dir lightrag[api]

# Copy config
COPY lightrag.yaml /app/lightrag.yaml

# Data volume
RUN mkdir -p /data

ENV LIGHTRAG_CONFIG=/app/lightrag.yaml
ENV LIGHTRAG_DATA_DIR=/data

EXPOSE 8000

CMD ["lightrag-api", "--host", "0.0.0.0", "--port", "8000"]
