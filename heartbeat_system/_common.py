"""===============================================================================

        FILE: heartbeat_system/_common.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-04-04T16:41:23.000842
    REVISION: ---

==============================================================================="""
import pymongo
import os
from datetime import datetime, timedelta
import pandas as pd


def get_mongo_client(coll_name="timers"):
    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    coll = client[os.environ.get("TIMERS_COLL", "timers")][coll_name]
    return client, coll


def get_timers(coll, now_jst=None, is_lte=True):
    if now_jst is None:
        now_jst = datetime.now()
    tasks_df = pd.DataFrame(coll.find({"$and": [
        {"datetime": {("$lte" if is_lte else "$gte"): now_jst}},
        {"status": {"$ne": "DONE"}},
    ]}))
    return tasks_df
