FROM python:3.9-slim

WORKDIR /app
COPY server/requirements.txt .
COPY server/server.py .
COPY common/ ./common/

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "server.py"]