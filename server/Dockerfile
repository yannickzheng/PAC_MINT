FROM python:3.9-slim
WORKDIR /server/
COPY ../requirements.txt .
COPY . /server/
EXPOSE 5555
RUN pip install --no-cache-dir -r requirements.txt
CMD python ./server.py
