# Dockerfile pour l'Agent IA Facebook

FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Repertoire de travail
WORKDIR /app

# Installation des dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements et installer les dependances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Creer les repertoires necessaires
RUN mkdir -p /app/data/documents /app/data/chroma_db /app/logs

# Exposer le port (Railway injecte $PORT)
EXPOSE ${PORT:-8000}

# Commande de demarrage — utilise $PORT de Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
