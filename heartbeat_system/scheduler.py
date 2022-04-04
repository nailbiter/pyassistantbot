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
from croniter import croniter
import _common

app = Flask(__name__)


@app.route("/list_habits")
def list_habits():
    _, coll = _common.get_mongo_client("habits")
    _, coll_anchors = _common.get_mongo_client("habit_anchors")
    habits_df = pd.DataFrame(coll.find())
    if len(habits_df) > 0:
        habits_df["text"] = habits_df.payload.apply(lambda o: o["text"])
        habits_df = habits_df.drop(
            columns=["payload", "url", "method", "_id", "start_date"])
#        habits_df.datetime = habits_df.datetime.apply(
#            lambda dt: dt.isoformat())
    return habits_df.to_json()


@app.route("/list_timers")
def list_timers():
    _, coll = _common.get_mongo_client()
    tasks_df = _common.get_timers(coll, is_lte=False)
    if len(tasks_df) > 0:
        tasks_df["text"] = tasks_df.payload.apply(lambda o: o["text"])
        tasks_df = tasks_df.drop(columns=["payload", "url", "method", "_id"])
        tasks_df.datetime = tasks_df.datetime.apply(lambda dt: dt.isoformat())
    return tasks_df.to_json()


@app.route('/heartbeat', methods=["POST"])
def heartbeat():
    logging.warning((request.form, os.environ["MONGO_URL"]))
    now_jst = datetime.fromisoformat(request.form["now"])
    logging.warning(now_jst)

    _, coll = _common.get_mongo_client()
    tasks_df = _common.get_timers(coll, now_jst=now_jst)
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

    _, coll = _common.get_mongo_client("habits")
    _, coll_anchors = _common.get_mongo_client("habit_anchors")
    habits_df = pd.DataFrame(coll.find())
    habit_anchors_df = pd.DataFrame(coll_anchors.find())
    habit_anchors = {}
    if len(habit_anchors_df) > 0:
        habit_anchors = {k: v for k, v in zip(
            habit_anchors_df.uuid, habit_anchors_df.datetime)}
    for habit in habits_df.to_dict(orient="records"):
        start_date = habit_anchors.get(habit["uuid"], habit["start_date"])
        base = start_date+timedelta(seconds=1)
        it = croniter(habit["cronline"], base)
        is_punched = False
        url = habit["url"]
        payload = habit["payload"]
        method = habit["method"]
        while (ds := it.get_next(datetime)) <= now_jst:
            is_punched = True
            getattr(requests, method.lower())(url, data=payload)
        if is_punched:
            coll_anchors.update_one(
                {"uuid": habit["uuid"]},
                {"$set": {"datetime": now_jst}},
                upsert=True,
            )

    return "Success"


@app.route('/register_single_call', methods=["POST"])
def register_single_call():
    _, coll = _common.get_mongo_client()
    form = request.form
    _uuid = str(uuid.uuid4())
    payload = form.get("payload")
    if payload is None:
        payload = "{}"
    logging.warning(f"payload: \"{payload}\"")
    # FIXME: subsample datetime to align with heartbeat freq
    coll.insert_one({
        "datetime": datetime.fromisoformat(form["datetime"]),
        "url": form["url"],
        "method": form["method"],
        "payload": json.loads(payload),
        "uuid": _uuid,
    })
    return _uuid


@app.route('/register_regular_call', methods=["POST"])
def register_regular_call():
    form = request.form
    cronline = form["cronline"]
    start_date = datetime.fromisoformat(form["start_date"])
    _, coll = _common.get_mongo_client("habits")
    _uuid = str(uuid.uuid4())
    payload = form.get("payload")
    if payload is None:
        payload = "{}"
    coll.insert_one({
        "uuid": _uuid,
        "url": form["url"],
        "start_date": start_date,
        "method": form["method"],
        "payload": json.loads(payload),
        "cronline": cronline,
    })
    return _uuid
