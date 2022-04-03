"""===============================================================================

        FILE: heartbeat_system/scheduler.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-03-08T20:51:45.256048
    REVISION: ---

==============================================================================="""
from flask import Flask, request
import logging
import os
from datetime import datetime, timedelta
import pymongo
import uuid
import json
import pandas as pd
import requests

app = Flask(__name__)


def _get_mongo_client():
    return pymongo.MongoClient(os.environ["MONGO_URL"])


@app.route('/heartbeat', methods=["POST"])
def heartbeat():
    logging.warning((request.form, os.environ["MONGO_URL"]))
    now_jst = datetime.fromisoformat(request.form["now"])
    logging.warning(now_jst)
    client = _get_mongo_client()
    coll = client["timers"]["timers"]
    tasks_df = pd.DataFrame(coll.find({"$and": [
        {"datetime": {"$lte": now_jst}},
        {"status": {"$ne": "DONE"}},
    ]}))
    logging.error(tasks_df.to_string())
    for r in tasks_df.to_dict(orient="records"):
        # make a call
        url = r["url"]
        payload = (r["payload"])
        method = r["method"]
        logging.warning((url, payload, method))
        getattr(requests, method.lower())(url, data=payload)

        # mark as done
        coll.update_one({"uuid": r["uuid"]}, {"$set": {"status": "DONE"}})
    return "Success"


@app.route('/register_single_call', methods=["POST"])
def register_single_call():
    client = _get_mongo_client()
    form = request.form
    _uuid = str(uuid.uuid4())
    payload = form.get("payload")
    if payload is None:
        payload = "{}"
    logging.warning(f"payload: \"{payload}\"")
    # FIXME: subsample datetime to align with heartbeat freq
    client["timers"]["timers"].insert_one({
        "datetime": datetime.fromisoformat(form["datetime"]),
        "url": form["url"],
        "method": form.get("method", "GET"),
        "payload": json.loads(payload),
        "uuid": _uuid,
    })
    return _uuid


@app.route('/register_regular_call', methods=["POST"])
def register_regular_call():
    # TODO
    return ""
