#!/usr/bin/env python3
"""===============================================================================

        FILE: heartbeat_system/heartbeat.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-03-08T20:50:01.478228
    REVISION: ---

==============================================================================="""

import click
#from dotenv import load_dotenv
import os
from os import path
import logging
import time
import requests
from datetime import datetime, timedelta
import math


def _wait_for_start_of_new_min():
    now = datetime.now()
    now_ = datetime.fromtimestamp(math.ceil(now.timestamp()/60)*60)
    logging.warning(f"going to sleep for {str(now_-now)}")
    time.sleep((now_-now).total_seconds())
    logging.warning(datetime.now().isoformat())


@click.command()
@click.option("-b", "--beat-duration-min", type=float, default=1)
@click.option("--remote-hostname", default="scheduler")
@click.option("--remote-port", type=int, default=5000)
@click.option("--remote-path", default="heartbeat")
@click.option("--wait-for-start-of-new-min/--no-wait-for-start-of-new-min", default=True)
def heartbeat(beat_duration_min, remote_hostname, remote_port, remote_path, wait_for_start_of_new_min):
    if wait_for_start_of_new_min:
        _wait_for_start_of_new_min()
    while True:
        now = datetime.now()
        now = datetime.fromtimestamp(
            now.timestamp()//(60*beat_duration_min)*(60*beat_duration_min))
        # TODO: re-sample the datetime object
        url = f"http://{remote_hostname}:{remote_port}/{remote_path}"
        #logging.warning(f"heartbeat {now.isoformat()}, url: \"{url}\"")
        try:
            requests.post(url, data={"now": now.isoformat()})
        except Exception as e:
            # FIXME: remove catch-all
            logging.error(e)
        time.sleep(60*beat_duration_min)


if __name__ == "__main__":
    #    if path.isfile(".env"):
    #        logging.warning("loading .env")
    #        load_dotenv()
    heartbeat()
