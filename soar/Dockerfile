FROM python:3.10-slim

RUN apt update && apt install -y iptables && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/log/soar

WORKDIR /soar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY config/ config/

EXPOSE 6000

CMD ["python", "app/main.py"]

