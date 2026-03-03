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
COPY data/ ./data/

# Creer les repertoires necessaires (si absents)
RUN mkdir -p /app/data/chroma_db /app/logs

# Pre-telecharger le modele fastembed au build (evite le download au runtime)
RUN python -c "from fastembed import TextEmbedding; list(TextEmbedding(model_name='BAAI/bge-small-en-v1.5').embed(['warmup']))"

# Exposer le port (Railway injecte $PORT)
EXPOSE ${PORT:-8000}

# Commande de demarrage — utilise $PORT de Railway
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
