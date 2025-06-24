FROM python:3.9-slim
WORKDIR /app
COPY site_web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY site_web/ .
EXPOSE 8080
CMD ["gunicorn","site_web.wsgi:application","--bind","0.0.0.0:8080"]