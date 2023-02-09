FROM ubuntu:20.04
COPY . .
RUN apt-get update
RUN apt-get install -y  \
            python3     \
            pip
RUN pip install -r requirements.txt

ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV DB_PATH=${DB_PATH}
ENV API_KEY=${API_KEY}
ENV API_SECRET=${API_SECRET}

ENTRYPOINT ["python3", "src/main.py"]
CMD ["bash"]