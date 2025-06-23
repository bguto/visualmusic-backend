FROM python:3.10-slim

# Instala herramientas necesarias
RUN apt-get update && \
    apt-get install -y ffmpeg git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Crea directorio para el código
WORKDIR /app

# Copia archivos
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto de Flask
EXPOSE 5000

# Comando para arrancar el backend
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
