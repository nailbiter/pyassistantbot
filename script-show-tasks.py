#!/usr/bin/env python3
"""===============================================================================

        FILE: script-show-tasks.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2021-12-20T21:49:40.453563
    REVISION: ---

==============================================================================="""

import click
#from dotenv import load_dotenv
import os
from os import path
import logging
import pandas as pd
import sqlite3
from scheduler import _get_current_tasks
import shlex
import json
from datetime import datetime


@click.command()
def script_show_tasks():
    df = _get_current_tasks()
    df["value"] = df["value"].apply(shlex.split).apply(
        lambda l: l[-2]).apply(json.loads).apply(lambda o: o["text"])
    df = df[["value", "due_date"]]
#    df.due_date = df.due_date.apply(
#        lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
    click.echo(df)


if __name__ == "__main__":
    #    if path.isfile(".env"):
    #        logging.warning("loading .env")
    #        load_dotenv()
    script_show_tasks()
