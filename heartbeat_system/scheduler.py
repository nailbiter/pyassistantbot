"""===============================================================================

        FILE: heartbeat_system/scheduler.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-03-08T20:51:45.256048
    REVISION: ---

==============================================================================="""
from flask import Flask, request
import logging
app = Flask(__name__)


@app.route('/heartbeat', methods=["POST"])
def hello_world():
    logging.warning(request.form)
    return 'Hello, World!'
