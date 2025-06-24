FROM python:3.9-slim

# Installer les dépendances nécessaires pour PyGame et Mesa
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsdl2-2.0-0 \
#    libsdl2-mixer-2.0-0 \
    mesa-utils \
    libgl1-mesa-dri \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les fichiers
COPY game/requirements.txt .
COPY game/ ./game/
COPY common/ ./common/
COPY images/ ./images/


# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurer l'environnement
ENV PYTHONPATH=/app
ENV DISPLAY=host.docker.internal:0.0

# Lancer pacmint.py
CMD ["python", "game/pacmint.py"]