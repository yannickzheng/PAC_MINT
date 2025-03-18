FROM python:3.9-slim
WORKDIR /game/
COPY ../requirements.txt /game
COPY . /game
COPY ../common/reseaux.py /game
COPY ../common/global_variable.py /game
RUN pip install --no-cache-dir -r requirements.txt
CMD python ./pacmint.py