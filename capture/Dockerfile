FROM python:3.10-slim

# Dépendances système nécessaires à scapy + mysql
RUN apt-get update && apt-get install -y \
    gcc \
    libpcap-dev \
    default-libmysqlclient-dev \
    pkg-config \
    iproute2 \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python
COPY capture/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier UNIQUEMENT ce qui est nécessaire
COPY capture/ capture/
COPY inference/ inference/
COPY models/ models/
COPY database/ database/
COPY data/processed/preprocessed_pipeline.pkl data/processed/preprocessed_pipeline.pkl
COPY preprocessed_data/ preprocessed_data/
COPY evaluate/ evaluate/

ENV PYTHONPATH=/app

CMD ["python", "-m", "capture.orchestrator_prediction"]
