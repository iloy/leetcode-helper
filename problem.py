#!/usr/bin/env python3

from enum import Enum, unique
import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME

@unique
class DifficultyEnum(str, Enum):
    Easy = 'Easy'
    Medium = 'Medium'
    Hard = 'Hard'

class Problem:
    def __init__(self, no: int, name: str, acceptance: float, difficulty: str, paidonly: bool, weblink: str):
        self.no = no
        self.name = name
        self.acceptance = acceptance
        self.difficulty = difficulty
        self.paidonly = paidonly
        self.weblink = weblink

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'Problem({self.no}, {self.name}, {self.difficulty})'

def get_problem(no: int) -> Optional[Problem]:
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute('SELECT * FROM problems WHERE id=?', (no,))
        row = cur.fetchone()

        if row is None:
            return None

        ret = Problem(row[0], row[1], row[2], row[3], row[4], row[5])
    finally:
        cur.close()
        con.close()

    return ret

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('invalid number of arguments')
        sys.exit(1)

    no = int(sys.argv[1])
    problem = get_problem(no)
    if problem is None:
        print('there is no such problem')
        sys.exit(1)

    print(problem.no, problem.name, problem.acceptance, problem.difficulty, 'plus' if problem.paidonly else 'free', problem.weblink)

