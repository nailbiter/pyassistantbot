FROM python:3.9-slim-buster
LABEL maintainer="nailbiter"

RUN apt-get update && apt-get install -y git curl

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY heartbeat.py .
COPY scheduler.py .
COPY _common.py .

ENV FLASK_APP="scheduler.py"

CMD ["flask", "run", "--host=0.0.0.0"]
