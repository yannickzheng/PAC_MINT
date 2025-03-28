FROM python:3.9-slim
WORKDIR /app
COPY . /app
ENV MODE=$mode
RUN pip install --no-cache-dire -r /app/requirements.txt
RUN pip install pygame
EXPOSE 5555
CMD ["python", "server/server.py"]