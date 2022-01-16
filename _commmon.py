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


def get_current_offset():
    # code below is adapted from https://stackoverflow.com/a/10854983
    offset = time.timezone if (
        time.localtime().tm_isdst == 0) else time.altzone
    offset_hour = int(offset / 60 / 60 * -1)
    return offset_hour
