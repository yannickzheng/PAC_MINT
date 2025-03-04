FROM python:3.9
WORKDIR /app
ARG mode=client
ENV MODE=$mode
COPY server /app/server
COPY game /app/game
COPY common /app/common
COPY images /app/images
COPY sound /app/sound
RUN if [ "$MODE" = "server" ]; then \
      rm -rf game common images sound; \
    else \
      rm -rf server; \
    fi
RUN pip install pygame
CMD ["sh", "-c", "if [ \"$MODE\" = 'server' ]; then python3 server/server.py; else python3 game/pacmint.py; fi"]
