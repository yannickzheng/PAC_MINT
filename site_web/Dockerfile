FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des fichiers statiques et migration
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate

# Entrée : démarrer avec gunicorn (PAS runserver)
CMD ["gunicorn", "site_web.wsgi:application", "--bind", "0.0.0.0:8000"]

EXPOSE 8000
