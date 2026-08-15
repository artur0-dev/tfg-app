FROM python:3.12-alpine

WORKDIR /app

# Dependencias del sistema:
# - iputils: provee el binario 'ping' en Alpine
# - build deps temporales para compilar bcrypt si no hay wheel musllinux disponible
RUN apk add --no-cache iputils && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Quitar las herramientas de compilación una vez instaladas las dependencias
RUN apk del .build-deps

COPY . .

RUN python init_db.py

EXPOSE 5000

CMD ["python","app.py"]
