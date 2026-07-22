FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema: iputils-ping provee el binario 'ping'
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_db.py

EXPOSE 5000

CMD ["python","app.py"]
