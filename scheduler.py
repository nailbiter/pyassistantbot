#!/usr/bin/env python3
"""===============================================================================

        FILE: scheduler.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2021-04-06T17:38:57.133197
    REVISION: ---

==============================================================================="""

import click
import sqlite3
import time
import pandas as pd
from datetime import datetime
import uuid
import json
import os
import math
from croniter import croniter
import logging


def _add_logger(f):
    logger = logging.getLogger(f.__name__)

    def _f(*args, **kwargs):
        return f(*args, logger=logger, **kwargs)
    _f.__name__ = f.__name__
    return _f


@click.group()
@click.option("-d", "--database-file", type=click.Path(), default="scheduler.db")
@click.option("-i", "--interval-min", type=int, default=1)
@click.pass_context
def scheduler(ctx, **kwargs):
    assert 60 > kwargs["interval_min"] > 0
    ctx.ensure_object(dict)
    ctx.obj["kwargs"] = {**kwargs}


def _create_tables(database_file):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id text PRIMARY KEY,
            due_date text NOT NULL,
            action text NOT NULL,
            cronline_id text
        );
    """)
    c.execute("""CREATE TABLE IF NOT EXISTS tasks_done (
            task_id text PRIMARY KEY,
            is_done bool NOT NULL
        );
    """)
    c.execute("""CREATE TABLE IF NOT EXISTS tasks_cronlines (
            cronline_id text PRIMARY KEY,
            cronline text NOT NULL
        );
    """)
    conn.close()


@scheduler.command()
@click.pass_context
def start(ctx,):
    kwargs = ctx.obj["kwargs"]
    _create_tables(kwargs["database_file"])
    while True:
        conn = sqlite3.connect(kwargs["database_file"])
        now_ = datetime.now()
        click.echo(f"now_: {now_.strftime('%Y%m%d%H%M')}")
        df = pd.read_sql_query(
            f"""
            SELECT * 
            FROM tasks left join tasks_done using (task_id) left join tasks_cronlines using (cronline_id) 
            WHERE is_done is null and due_date<="{now_.strftime('%Y%m%d%H%M')}"
            """,
            conn
        )
        conn.close()

        for r in df.to_dict(orient="records"):
            action = json.loads(r["action"])
            if action["tag"] == "shell":
                os.system(action["value"])
            click.echo(f"TODO: {r}")

        conn = sqlite3.connect(kwargs["database_file"])
        pd.DataFrame({"task_id": df["task_id"], "is_done": True}).to_sql(
            'tasks_done', conn, if_exists='append', index=None)
        conn.close()

        seconds_to_sleep = interval_min*60 - (datetime.now()-now_).seconds
        if seconds_to_sleep > 0:
            time.sleep(seconds_to_sleep)


def _schedule(database_file, due_date, action, cron_line=None):
    kwargs = {"due_date": due_date, "action": action}
    kwargs["due_date"] = kwargs["due_date"].strftime("%Y%m%d%H%M")
    conn = sqlite3.connect(database_file)
    pd.DataFrame([{"task_id": str(uuid.uuid4()), **kwargs}]
                 ).to_sql('tasks', conn, if_exists='append', index=None)
    conn.close()


@scheduler.command()
@click.pass_context
@click.option("-t", "--tag", type=click.Choice(["shell"]), default="shell")
@click.option("-v", "--value", required=True)
@click.option("-d", "--due-date", type=click.DateTime(), required=True)
@click.option("-c", "--cron-line")
@click.option("--auto-fix/--no-auto-fix", default=False)
@_add_logger
def schedule(ctx, due_date, value, tag, auto_fix, cron_line, logger=None):
    kwargs_ = ctx.obj["kwargs"]
    interval_min = kwargs_["interval_min"]
    aligned_date = due_date.replace(minute=math.ceil(
        due_date.minute/interval_min) * interval_min)
    if due_date != aligned_date:
        if auto_fix:
            logger.info(
                f"replace due_date {due_date.isoformat()} with {aligned_date.isoformat()}")
            due_date = aligned_date
        else:
            assert False, f"replace due_date {due_date.isoformat()} with {aligned_date.isoformat()}"
    if cron_line is not None:
        c = croniter(cron_line)
        d = c.get_next(datetime)
        remainder = (c.get_next(datetime, start_time=d) -
                     d).seconds % (60*interval_min)
        assert remainder == 0, (cron_line, remainder)

    _schedule(kwargs["database_file"], due_date=due_date,
              action={"tag": tag, "value": value}, cron_line=cron_line)


if __name__ == "__main__":
    scheduler()
