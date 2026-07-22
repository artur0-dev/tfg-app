FROM python:3.12-slim

WORKDIR /app

# Actualizar paquetes del SO a las últimas versiones parcheadas disponibles
# + instalar iputils-ping, minimizando lo instalado
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends iputils-ping && \
    apt-get purge -y --auto-remove perl-base || true && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Actualizar pip antes de instalar dependencias (corrige CVEs de pip)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_db.py

EXPOSE 5000

CMD ["python","app.py"]
