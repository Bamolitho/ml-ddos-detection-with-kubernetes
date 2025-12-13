# FROM baseImage:tag
FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*


# Metadata
LABEL maintainer="Amolitho"
LABEL version="1.0"
LABEL description="ML DDoS detection"

# Set Environment variables
ENV PORT=6000

# Working directory
WORKDIR /web

# Installe curl avant de créer l'utilisateur non-root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Define which user runs inside
RUN useradd -m appuser
USER appuser

# COPY requirements.txt from the directiry where Dockerfile is
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# COPY <src> <dst> (second . = /app)
COPY . .

# Tells docker which port the container listens on (API port)
EXPOSE 6000

# [INFO] Variables d'environnement pour Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:6000/health || exit 1
  

# Define what command runs when the container starts
ENTRYPOINT [ "python" ] 
CMD ["app.py"]
