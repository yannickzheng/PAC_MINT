FROM python:3.9-slim

# Install system dependencies for pygame
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY server/requirements.txt .
COPY common/ ./common/
COPY server/ ./server/
COPY game/ ./game/
COPY images/ ./images/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Configure PYTHONPATH
ENV PYTHONPATH=/app

# Run server.py
CMD ["python", "server/server.py"]