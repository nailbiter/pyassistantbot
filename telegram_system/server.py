"""===============================================================================

        FILE: telegram_system/server.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-04-02T22:56:29.570874
    REVISION: ---

==============================================================================="""
from flask import Flask, request
import logging
import os
import requests
import json
import re
from datetime import datetime, timedelta
import _common

app = Flask(__name__)


@app.route('/new_habit', methods=["POST"])
def new_habit():
    #    logging.warning((request.form, os.environ["MONGO_URL"]))
    message = json.loads(request.form["message"])
    chat_id = message["chat"]["id"]
    text = message["text"]
    _, c1, c2, c3, c4, c5, media, msg = re.split(r"\s+", text, maxsplit=8)
    url = f"http://{os.environ['SCHEDULER']}/register_regular_call"
    _url = f"http://{os.environ['SELF_URL']}/send_message"
    payload = {
        "text": msg,
        "chat_id": chat_id,
    }
    kwargs = {
        "cronline": " ".join([c1, c2, c3, c4, c5]),
        "start_date": datetime.now().isoformat(),
    }
    requests.post(url, data={
        "url": _url,
        "method": "POST",
        "payload": json.dumps(payload),
        **kwargs,
    })
    return 'Hello, World!'


@app.route('/new_timer', methods=["POST"])
def new_timer():
    logging.warning((request.form, os.environ["MONGO_URL"]))
    message = json.loads(request.form["message"])
    chat_id = message["chat"]["id"]
    text = message["text"]
    _, time, media, msg = re.split(r"\s+", text, maxsplit=4)
    url = f"http://{os.environ['SCHEDULER']}/register_single_call"
    _url = f"http://{os.environ['SELF_URL']}/send_message"
    payload = {"text": msg, "chat_id": chat_id}
    requests.post(url, data={"datetime": _common.parse_time(
        time).isoformat(), "url": _url, "method": "POST", "payload": json.dumps(payload)})
    return 'Hello, World!'


@app.route("/send_message", methods=["POST"])
def send_message():
    form = request.form
    _common.send_message(form["chat_id"], form["text"])
    return "Success"
