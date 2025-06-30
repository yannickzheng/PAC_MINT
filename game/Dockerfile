FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsdl2-2.0-0 \
    mesa-utils \
    libgl1-mesa-dri \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY game/requirements.txt .
COPY game/ ./game/
COPY common/ ./common/
COPY images/ ./images/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV DISPLAY=host.docker.internal:0.0

CMD ["python", "game/pacmint.py"]