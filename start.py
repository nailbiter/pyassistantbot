#!/usr/bin/env python3
"""===============================================================================

        FILE: start.py

       USAGE: ./start.py

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2021-04-29T16:18:19.680930
    REVISION: ---

==============================================================================="""

import click
from scheduler import start_scheduler
from concurrent import futures
import logging
from telegram_client import telegram_client
from dotenv import load_dotenv
from os import path

_WHAT = {
    "scheduler": start_scheduler,
    "telegram": telegram_client,
}


@click.command()
@click.option("-w", "--what", type=click.Choice(_WHAT), multiple=True)
@click.option("--debug/--no-debug", default=False)
def start(what, debug):
    if debug:
        logging.basicConfig(level=logging.INFO)
    what = set(what)
    if len(what) == 0:
        what = set(_WHAT)
    click.echo(what)
    with futures.ProcessPoolExecutor() as ex:
        for k in what:
            f = _WHAT[k]
            click.echo(f"k: {k} => {f.__name__}")
            ex.submit(f, logger=logging.getLogger(f.__name__))


if __name__ == "__main__":
    if path.isfile(".env"):
        logging.warning("loading .env")
        load_dotenv()
    start()
