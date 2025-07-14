FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet Django
COPY . .

# Collecte des fichiers statiques (ne plante pas même si le dossier est vide)
RUN python manage.py collectstatic --noinput || true

# Expose le port 8080
EXPOSE 8080

# Commande de démarrage : gunicorn sur le port 8080
CMD ["gunicorn", "site_web.wsgi:application", "--bind", "0.0.0.0:8080"]
