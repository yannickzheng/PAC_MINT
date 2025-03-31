FROM python:3.9-slim

WORKDIR /app
COPY game/requirements.txt .
COPY game/pacmint.py .
COPY common/ ./common/
COPY ./ .

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "pacmint.py"]