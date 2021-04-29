"""===============================================================================

        FILE: telegram_client.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2021-04-29T17:27:34.152166
    REVISION: ---

==============================================================================="""

import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext import MessageHandler, Filters
import logging
from scheduler import schedule
from datetime import datetime, timedelta


def _add_logger(f):
    logger = logging.getLogger(f.__name__)

    def _f(*args, **kwargs):
        return f(*args, logger=logger, **kwargs)
    _f.__name__ = f.__name__
    return _f


class _NewTimer:
    def __init__(self, telegram_token):
        self._telegram_token = telegram_token
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, update, context):
        logger = self._logger
        _, time, media, msg = update.message.text.split(" ", maxsplit=3)
        media = media[1:]
        chat_id = update.effective_chat.id
        logger.info(f"chat_id: {chat_id}")
#        assert media in ["slack", "telegram"], media
        assert media in ["telegram", ], media
        if media == "telegram":
            media = f"{media}:{update.effective_chat.id}"
        dt = datetime.now()
        if time.startswith("+"):
            dt += timedelta(minutes=int(time[1:]))
        else:
            time_chunks = [time[i:i+2] for i in range(0, len(time), 2)]
            time_chunks = reversed(time_chunks)
            for tc, flag in zip(time_chunks, "minute hour day month year".split(" ")):
                dt = dt.replace(
                    **{flag: (2000 if flag == "year" else 0)+int(tc)})
        dt.replace(second=0,microsecond=0)

        cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{{\"chat_id\": \"{chat_id}\", \"text\": \"{msg}\"}}' https://api.telegram.org/bot{self._telegram_token}/sendMessage"
        schedule(due_date=dt, action={
                 "tag": "shell", "value": cmd})


def telegram_client(logger, token=os.environ["TELEGRAM_TOKEN"]):
    updater = Updater(token, use_context=True)
    if updater.bot is None:
        print("bot is None!!")
    bot = updater.bot

    updater.dispatcher.add_handler(CommandHandler(
        'new_timer', _NewTimer(telegram_token=token)))
#
#    # Start the Bot
    updater.start_polling()
