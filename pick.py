#!/usr/bin/env python3

from enum import Enum, unique
import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME
from problem import Problem, DifficultyEnum
from util import strfdelta

@unique
class StatusEnum(str, Enum):
    Unsolved = 'Unsolved'
    Solved = 'Solved'

@unique
class BillingEnum(str, Enum):
    Free = 'Free'
    Plus = 'Plus'

def load_problem(query: str) -> Tuple[Optional[Problem], bool, str]:
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute(query)
        row = cur.fetchone()

        if row is None:
            return None, False, ''

        ret = Problem(row[0], row[1], row[2], row[3], row[4], row[5])
        solved = True if row[6] is not None else False
        time_start = row[7]
        time_done = row[8]
        if time_start and time_done:
            time_elapsed = strfdelta(row[7], row[8])
        else:
            time_elapsed = ''
    finally:
        cur.close()
        con.close()

    return ret, solved, time_elapsed

def pick_problem(target_difficulties: List[DifficultyEnum], target_status: List[StatusEnum], target_billing: List[BillingEnum]) -> Tuple[Optional[Problem], bool, str]:
    if len(target_difficulties) == 0:
        return None, False, ''

    if len(target_status) == 0:
        return None, False, ''

    if len(target_billing) == 0:
        return None, False, ''

    for d in target_difficulties:
        assert d in DifficultyEnum

    for s in target_status:
        assert s in StatusEnum

    for b in target_billing:
        assert b in BillingEnum

    cond = '(' + ' OR '.join(['difficulty = \'' + d.value + '\'' for d in target_difficulties]) + ')'

    if 'Unsolved' in target_status and 'Solved' in target_status:
        pass
    elif 'Unsolved' in target_status:
        cond = cond + ' AND solved.id IS NULL'
    elif 'Solved' in target_status:
        cond = cond + ' AND solved.id IS NOT NULL'
    else:
        assert False

    if 'Free' in target_billing and 'Plus' in target_billing:
        pass
    elif 'Free' in target_billing:
        cond = cond + ' AND problems.plus = 0'
    elif 'Plus' in target_billing:
        cond = cond + ' AND problems.plus = 1'
    else:
        assert False

    problem, solved, time_elapsed = load_problem('SELECT problems.*, solved.id, solved.time_start, solved.time_done FROM problems LEFT JOIN solved ON solved.id = problems.id LEFT JOIN excluded ON excluded.id = problems.id WHERE excluded.id IS NULL AND ' + cond  + ' ORDER BY RANDOM() LIMIT 1')

    return problem, solved, time_elapsed

if __name__ == '__main__':

    target_difficulties = [DifficultyEnum.Easy]
    target_status = [StatusEnum.Unsolved]
    target_billing = [BillingEnum.Free]

    problem, solved, time_elapsed = pick_problem(target_difficulties, target_status, target_billing)
    if problem is None:
        print('there is no candidate problem')
        sys.exit(1)

    print(problem.no, problem.name, problem.acceptance, problem.difficulty)

