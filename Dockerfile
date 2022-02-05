FROM python:3.9-slim-buster
LABEL maintainer="nailbiter"

RUN apt-get update && apt-get install -y git curl

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY scheduler.py scheduler.py
#COPY script-show-tasks.py script-show-tasks.py
COPY _common.py _common.py
COPY telegram_client.py telegram_client.py

COPY .envrc .env

CMD ["python3","start.py","--debug"]
