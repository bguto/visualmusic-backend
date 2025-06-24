# Dockerfile
FROM python:3.10-slim

# 1) Instala dependencias del sistema (ffmpeg + libsndfile)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libsndfile1 \
      libsndfile1-dev \
      build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copia los requisitos y los instala
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3) Copia el resto del código
COPY . .

# 4) Expone el puerto
EXPOSE 5000

# 5) Arranca con Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
