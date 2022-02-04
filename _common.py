"""===============================================================================

        FILE: _commmon.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2022-01-16T14:37:32.761395
    REVISION: ---

==============================================================================="""
import time
from os import path
import json


def get_current_offset():
    # code below is adapted from https://stackoverflow.com/a/10854983
    offset = time.timezone if (
        time.localtime().tm_isdst == 0) else time.altzone
    offset_hour = int(offset / 60 / 60 * -1)
    return offset_hour


_CONFIG_FILENAME = "/data/.config.json"


def get_config():
    if not path.isfile(_CONFIG_FILENAME):
        return {}
    else:
        config = {}
        with open(_CONFIG_FILENAME) as f:
            config = json.load(f)
        return config


def update_config(**update):
    config = get_config()
    with open(_CONFIG_FILENAME, "w") as f:
        config = json.dump({**config, **update}, f, indent=2, sort_keys=True)


def simple_math_eval(s, number_utils=(float, float)):
    s = list(s[::-1])
    string_to_num, float_to_num = number_utils

    def get_value():
        sign = 1
        if s and s[-1] == "-":
            s.pop()
            sign = -1
        value = 0
        while s and s[-1].isdigit():
            value *= 10
            value += string_to_num(s.pop())
        return sign * value

    def get_term():
        term = get_value()
        while s and s[-1] in "*/":
            op = s.pop()
            value = get_value()
            if op == "*":
                term *= value
            else:
                term = float_to_num(1.0 * term / value)
        return term

    ans = get_term()
    while s:
        op, term = s.pop(), get_term()
        if op == "+":
            ans += term
        else:
            ans -= term
    return ans
