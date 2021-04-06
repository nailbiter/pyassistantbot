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


@click.group()
@click.option("--database-file",type=click.Path(),default="scheduler.db")
@click.option("--interval-min",type=int,default=5)
@click.pass_context
def scheduler(ctx,**kwargs):
    ctx.ensure_object(dict)
    ctx.obj["kwargs"] = {**kwargs}


@scheduler.command()
@click.pass_context
def start(ctx,):
    kwargs = ctx.obj["kwargs"]
    while True:
        time.sleep(60*kwargs["interval_min"])
		conn = sqlite3.connect(kwargs["database_file"])
		df=pd.read_sql_query("""SELECT * FROM tasks left""", conn)
#		conn = sqlite3.connect(file_sqlite3)
#		df.to_sql('cities',conn,if_exists='append',index=None)
        conn.close()


@scheduler.command()
@click.pass_context
def schedule(ctx,):
    pass


if __name__ == "__main__":
    scheduler()
