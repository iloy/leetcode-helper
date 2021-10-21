#!/usr/bin/env python3

from datetime import datetime, timedelta
import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME, vacuum
from util import strfdelta

def update_time_done(no: int, time_done: Optional[str] = None) -> Tuple[str, str, str]:
    if time_done is None:
        time_done = '(DATETIME(\'now\', \'localtime\'))'

    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute('UPDATE solved SET time_done='+ time_done +' WHERE id=?', (no,))
        assert cur.rowcount == 1

        con.commit()

        cur.execute('SELECT time_start, time_done FROM solved WHERE id=?', (no,))
        row = cur.fetchall()
        assert len(row) == 1
        assert len(row[0]) == 2
    finally:
        cur.close()
        con.close()

    time_start, time_done = str(row[0][0]), str(row[0][1])
    time_elapsed = strfdelta(time_start, time_done)

    return time_start, time_done, time_elapsed

if __name__ == '__main__':

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('invalid argument')
        sys.exit(1)

    no = int(sys.argv[1])
    time_done = '(DATETIME(\'now\', \'localtime\'))'

    if len(sys.argv) == 3:
        time_done = '\'' + sys.argv[2] + '\''

    time_start, time_done, time_elapsed = update_time_done(no, time_done)
    vacuum()

    print('start time:', time_start)
    print('end time:  ', time_done)
    print('elapsed time:', time_elapsed)

