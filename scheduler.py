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
from datetime import datetime, timedelta
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


_DEFAULTS = {
    "database_file": "scheduler.db",
    "interval_min": 1
}


@click.group()
@click.option("-d", "--database-file", type=click.Path(), default=_DEFAULTS["database_file"])
@click.option("-i", "--interval-min", type=int, default=_DEFAULTS["interval_min"])
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def scheduler(ctx, debug, **kwargs):
    assert 60 > kwargs["interval_min"] > 0
    if debug:
        logging.basicConfig(level=logging.INFO)
    ctx.ensure_object(dict)
    ctx.obj["kwargs"] = {**kwargs}


def _create_tables(database_file):
    logger.info(f"before connect to {database_file}")
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    logger.info("before _create_tables")
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id text PRIMARY KEY,
            due_date text NOT NULL,
            action text NOT NULL,
            cronline_id text
        );
    """)
    logger.info("after t1")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks_done (
            task_id text PRIMARY KEY,
            is_done bool NOT NULL
        );
    """)
    logger.info("after t2")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks_cronlines (
            cronline_id text PRIMARY KEY,
            cronline text NOT NULL
        );
    """)
    logger.info("after t3")
    conn.close()


def _get_current_tasks(database_file=_DEFAULTS["database_file"], now_=None, pretty=True):
    conn = sqlite3.connect(database_file)
    sql = f"""
        SELECT * 
        FROM tasks left join tasks_done using (task_id) left join tasks_cronlines using (cronline_id) 
        WHERE is_done is null
        """
    if now_ is not None:
        sql += f""" and due_date<="{now_.strftime('%Y%m%d%H%M')}" """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    if pretty:
        df.due_date = df.due_date.apply(
            lambda s: datetime.strptime(s, "%Y%m%d%H%M"))
        actions_df = pd.DataFrame(list(df.pop("action").apply(json.loads)))
        for c in actions_df:
            df = pd.DataFrame({**df, **actions_df})

    return df


def start_scheduler(logger, interval_min=_DEFAULTS["interval_min"], database_file=_DEFAULTS["database_file"]):
    logger.info("start")
    _create_tables(database_file)
    logger.info("after _create_tables")
    while True:
        conn = sqlite3.connect(database_file)
        click.echo(f"now_: {now_.strftime('%Y%m%d%H%M')}")
        df = _get_current_tasks(
            database_file=database_file, now_=now_, pretty=False)

        for r in df.to_dict(orient="records"):
            action = json.loads(r["action"])
            logger.info(f"action: {action}")
            if action["tag"] == "shell":
                os.system(action["value"])
            click.echo(f"TODO: {r}")
            if r["cronline"] is not None:
                c = croniter(r["cronline"])
                # FIXME: compensate for dolg
#                d = c.get_next(datetime,start_time=datetime.strptime(r["due_date"],"%Y%m%d%H%M"))
                d = c.get_next(datetime, start_time=now_)
                schedule(database_file=database_file, action=action,
                         due_date=d, cronline_id=r["cronline_id"])

        conn = sqlite3.connect(database_file)
        pd.DataFrame({"task_id": df["task_id"], "is_done": True}).to_sql(
            'tasks_done', conn, if_exists='append', index=None)
        conn.close()

        seconds_to_sleep = interval_min*60 - (datetime.now()-now_).seconds
        if seconds_to_sleep > 0:
            time.sleep(seconds_to_sleep)


@scheduler.command()
@click.pass_context
def start(ctx):
    kwargs = ctx.obj["kwargs"]
    start_scheduler(logger=logging.getLogger(
        start_scheduler.__name__), **kwargs)


def schedule(due_date, action, cron_line=None, cronline_id=None, database_file=_DEFAULTS["database_file"]):
    logger = logging.getLogger("schedule")
    kwargs = {"due_date": due_date, "action": json.dumps(action)}
    logger.info(f"kwargs: {kwargs}")
    kwargs["due_date"] = kwargs["due_date"].strftime("%Y%m%d%H%M")
    if cronline_id is None:
        cronline_id = str(uuid.uuid4())
    if cron_line is not None or cronline_id is not None:
        kwargs["cronline_id"] = cronline_id

    conn = sqlite3.connect(database_file)

#    click.echo(kwargs)
    pd.DataFrame([{"task_id": str(uuid.uuid4()), **kwargs}]
                 ).to_sql('tasks', conn, if_exists='append', index=None)
    if cron_line is not None:
        pd.DataFrame([{"cronline": cron_line, "cronline_id": kwargs["cronline_id"]}]
                     ).to_sql('tasks_cronlines', conn, if_exists='append', index=None)
    conn.close()


@scheduler.command(name="schedule")
@click.pass_context
@click.option("-t", "--tag", type=click.Choice(["shell"]), default="shell")
@click.option("-v", "--value", required=True)
@click.option("-d", "--due-date", type=click.DateTime())
@click.option("-m", "--minutes-delay", type=int)
@click.option("-c", "--cron-line")
@click.option("--auto-fix/--no-auto-fix", default=False)
def schedule_click(ctx, value, tag, auto_fix, cron_line, **kwargs):
    logger = logging.getLogger("schedule_click")

    assert sum([(1 if (kwargs[k] is not None) else 0) for k in "minutes_delay,due_date".split(
        ",")]) == 1, f"exactly one of minutes_delay,due_date should be given"
    if kwargs["due_date"] is not None:
        due_date = kwargs["due_date"]
    elif kwargs["minutes_delay"] is not None:
        due_date = datetime.now() + timedelta(minutes=kwargs["minutes_delay"])

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

    schedule(database_file=kwargs_["database_file"], due_date=due_date,
             action={"tag": tag, "value": value}, cron_line=cron_line)


if __name__ == "__main__":
    scheduler()
