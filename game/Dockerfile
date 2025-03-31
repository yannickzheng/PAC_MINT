FROM python:3.9-slim

WORKDIR /app
COPY game/requirements.txt .
COPY game/ ./game/
COPY common/ ./common/
COPY images/ ./images/
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
CMD ["python", "game/pacmint.py"]