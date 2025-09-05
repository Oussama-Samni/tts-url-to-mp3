# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Evitar prompts de apt
ENV DEBIAN_FRONTEND=noninteractive

# 1) Paquetes del sistema que necesitamos:
#    - ffmpeg: lo usa pydub para exportar/leer audio
#    - libxml2/libxslt: dependencias nativas de lxml/newspaper3k (estabilidad)
#    - ca-certificates/curl: TLS y utilidades básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates curl libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# 2) Directorio de trabajo dentro del contenedor
WORKDIR /app

# 3) Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copiar tu código al contenedor
COPY . .

# 5) Hugging Face Spaces define $PORT.
#    Usamos gunicorn para servir Flask en 0.0.0.0:$PORT
ENV PORT=7860
CMD ["bash", "-lc", "gunicorn app_web:app -b 0.0.0.0:$PORT --timeout 180 --workers 1 --threads 4"]
