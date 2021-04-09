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


@click.group()
@click.option("--database-file", type=click.Path(), default="scheduler.db")
@click.option("--interval-min", type=int, default=1)
@click.pass_context
def scheduler(ctx, **kwargs):
    assert kwargs["interval_min"] > 0
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
        now_ = datetime.now().strftime("%Y%m%d%H%M")
        click.echo(f"now_: {now_}")
        df = pd.read_sql_query(
            f"""
            SELECT * 
            FROM tasks left join tasks_done using (task_id) left join tasks_cronlines using (cronline_id) 
            WHERE is_done is null and due_date<="{now_}"
            """,
            conn
        )
        conn.close()

        for r in df.to_dict(orient="records"):
            click.echo(f"TODO: {r}")

        conn = sqlite3.connect(kwargs["database_file"])
        pd.DataFrame({"task_id": df["task_id"], "is_done": True}).to_sql(
            'tasks_done', conn, if_exists='append', index=None)
        conn.close()

        # FIXME: wait only if need to
        time.sleep(60*kwargs["interval_min"])


def _schedule(database_file, due_date, action):
    kwargs = {"due_date": due_date, "action": action}
    kwargs["due_date"] = kwargs["due_date"].strftime("%Y%m%d%H%M")
    conn = sqlite3.connect(database_file)
    pd.DataFrame([{"task_id": str(uuid.uuid4()), **kwargs}]
                 ).to_sql('tasks', conn, if_exists='append', index=None)
    conn.close()


@scheduler.command()
@click.pass_context
@click.option("-a", "--action")
@click.option("-d", "--due-date", type=click.DateTime())
def schedule(ctx, **kwargs):
    kwargs_ = ctx.obj["kwargs"]
    _schedule(kwargs["database_file"], **kwargs)


if __name__ == "__main__":
    scheduler()
