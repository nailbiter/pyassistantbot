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
from datetime import datetime


@click.command()
@click.option("-b", "--beat-duration-min", type=float, default=1)
@click.option("--remote-hostname", default="scheduler")
@click.option("--remote-port", type=int, default=5000)
@click.option("--remote-path", default="heartbeat")
def heartbeat(beat_duration_min, remote_hostname, remote_port, remote_path):
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
