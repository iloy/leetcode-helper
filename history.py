#!/usr/bin/env python3

import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME
from problem import Problem
from util import strfdelta

class History:
    def __init__(self, problem: Problem, time_start: str, time_done: str):
        self.problem = problem
        self.time_start = time_start
        if time_done:
            self.time_done = time_done
            self.time_elapsed = strfdelta(time_start, time_done)
        else:
            self.time_done = ''
            self.time_elapsed = ''

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'History({self.problem}, {self.time_start}, {self.time_done}, {self.time_elapsed})'

def get_history(start: str = '', end: str = '', reverse: bool = False) -> List[History]:
    where = ''

    if len(start) > 0 and len(end) > 0:
        where = f'AND \'{start}\' <= time_start AND time_start <= \'{end}\''
    elif len(start) > 0:
        where = f'AND \'{start}\' <= time_start'
    elif len(end) > 0:
        where = f'AND time_start <= \'{end}\''

    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        query = 'SELECT problems.*, solved.time_start, solved.time_done FROM problems LEFT JOIN solved ON problems.id = solved.id WHERE solved.time_start IS NOT NULL ' + where + ' ORDER BY solved.time_start ' + ('DESC' if reverse else 'ASC')
        cur.execute(query)
        rows = cur.fetchall()
    finally:
        cur.close()
        con.close()

    ret: List[History] = []
    for row in rows:
        p = Problem(row[0], row[1], row[2], row[3], False if row[4] == 0 else True, row[5])
        ret.append(History(p, row[6], row[7]))

    return ret

if __name__ == '__main__':

    if len(sys.argv) > 3:
        print('invalid number of arguments')
        sys.exit(1)

    start, end = '', ''

    if len(sys.argv) >= 2:
        start = sys.argv[1]
    if len(sys.argv) == 3:
        end = sys.argv[2]

    history = get_history(start, end)
    for h in history:
        print(h)

