FROM python:3.9-slim

WORKDIR /app

# Copier les fichiers
COPY server/requirements.txt .
COPY server/server.py .
COPY common/ ./common/
COPY server/rooms.py .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lancer server.py
CMD ["python", "server.py"]

