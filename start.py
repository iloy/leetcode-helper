#!/usr/bin/env python3

import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME, vacuum

def insert_time_start(no: int, start_again: bool = False, time_start: str = '(DATETIME(\'now\', \'localtime\'))') -> str:
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        if start_again:
            cur.execute('UPDATE solved SET time_start = '+ time_start +', time_done = NULL WHERE id = ?', (no,))
        else:
            cur.execute('INSERT INTO solved (id, time_start) VALUES (?, '+ time_start +')', (no,))
        assert cur.rowcount == 1

        cur.execute('SELECT time_start FROM solved WHERE id=?', (no,))
        row = cur.fetchall()
#        print(no, len(row))
        assert len(row) == 1
        assert len(row[0]) == 1

        con.commit()
    finally:
        cur.close()
        con.close()

    return str(row[0][0])

if __name__ == '__main__':

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('invalid argument')
        sys.exit(1)

    no = int(sys.argv[1])
    time_start = '(DATETIME(\'now\', \'localtime\'))'

    if len(sys.argv) == 3:
        time_start = '\'' + sys.argv[2] + '\''

    time_start = insert_time_start(no, False, time_start)
    vacuum()

    print('start time:', time_start)

