# Usa una imagen base ligera de Python 3.10
FROM python:3.10-slim

# 1) Instala herramientas del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libsndfile1 \
      libsndfile1-dev \
      git \
      build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2) Crea y establece el directorio de trabajo
WORKDIR /app

# 3) Copia primero solo requirements.txt y lo instala (cache friendly)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4) Ahora copia el resto del código de tu backend
COPY . /app

# 5) Expone el puerto que usa tu Flask/Gunicorn
EXPOSE 5000

# 6) Comando por defecto para lanzar tu app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
