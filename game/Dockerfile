FROM python:3.9-slim

# Dépendances système nécessaires à Pygame
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    mesa-utils \
    libgl1-mesa-dri \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY game/requirements.txt ./requirements.txt
COPY game/ ./game/
COPY common/ ./common/
COPY images/ ./images/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Définir les variables d’environnement
ENV PYTHONPATH=/app
ENV DISPLAY=host.docker.internal:0.0

# Lancer le jeu
CMD ["python", "game/pacmint.py"]
