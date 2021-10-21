#!/usr/bin/env python3

import sqlite3
import sys
from typing import *

from database import DATABASE_FILENAME

def load_stats_simple(query: str) -> Any:
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute(query)
        rows = cur.fetchall()
    finally:
        cur.close()
        con.close()

    return rows

def load_stats_easy_medium_hard(query: str) -> Tuple[int, int, int]:
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute(query)
        rows = cur.fetchall()
    finally:
        cur.close()
        con.close()

    easy, medium, hard = 0, 0, 0
    for row in rows:
        if row[0] == 'Easy':
            easy = int(row[1])
        elif row[0] == 'Medium':
            medium = int(row[1])
        elif row[0] == 'Hard':
            hard = int(row[1])
        else:
            assert False

    return (easy, medium, hard)

def load_stats() -> Dict[str, Any]:
    # total_[easy/medium/hard]
    # solved_[easy/medium/hard]
    # total_free_[easy/medium/hard]
    # solved_free_[easy/medium/hard]
    total_easy, total_medium, total_hard = load_stats_easy_medium_hard('SELECT difficulty, COUNT(id) FROM problems GROUP BY difficulty')
    solved_easy, solved_medium, solved_hard = load_stats_easy_medium_hard('SELECT problems.difficulty, COUNT(solved.id) FROM solved LEFT JOIN problems ON problems.id = solved.id WHERE solved.time_done IS NOT NULL GROUP BY problems.difficulty')
    total_free_easy, total_free_medium, total_free_hard = load_stats_easy_medium_hard('SELECT difficulty, COUNT(id) FROM problems WHERE id NOT IN (SELECT id FROM excluded) AND plus = 0 GROUP BY difficulty')
    solved_free_easy, solved_free_medium, solved_free_hard = load_stats_easy_medium_hard('SELECT problems.difficulty, COUNT(solved.id) FROM solved LEFT JOIN problems ON problems.id = solved.id WHERE solved.time_done IS NOT NULL AND solved.id NOT IN (SELECT id FROM excluded) GROUP BY problems.difficulty')

    # today_[easy/medium/hard]
    # total_open
    today_easy, today_medium, today_hard = load_stats_easy_medium_hard('SELECT difficulty, COUNT(id) FROM problems WHERE id IN (SELECT id FROM solved WHERE (DATE(time_done)) = (DATE(\'now\', \'localtime\'))) GROUP BY difficulty')
    total_open = [(row[0], row[1]) for row in load_stats_simple('SELECT id, time_start FROM solved WHERE time_done IS NULL order by time_start ASC')]

    d: Dict[str, Any] = {}

    d['total_easy'] = total_easy
    d['total_medium'] = total_medium
    d['total_hard'] = total_hard

    d['solved_easy'] = solved_easy
    d['solved_medium'] = solved_medium
    d['solved_hard'] = solved_hard

    d['total_free_easy'] = total_free_easy
    d['total_free_medium'] = total_free_medium
    d['total_free_hard'] = total_free_hard

    d['solved_free_easy'] = solved_free_easy
    d['solved_free_medium'] = solved_free_medium
    d['solved_free_hard'] = solved_free_hard

    d['today_easy'] = today_easy
    d['today_medium'] = today_medium
    d['today_hard'] = today_hard

    d['total_open'] = total_open

    return d

if __name__ == '__main__':

    if len(sys.argv) != 1:
        print('invalid number of arguments')
        sys.exit(1)

    stats = load_stats()
    print('Easy:', stats['solved_easy'], '/', stats['total_easy'], '(', stats['solved_free_easy'], '/', stats['total_free_easy'], ')')
    print('Medium:', stats['solved_medium'], '/', stats['total_medium'], '(', stats['solved_free_medium'], '/', stats['total_free_medium'], ')')
    print('Hard:', stats['solved_hard'], '/', stats['total_hard'], '(', stats['solved_free_hard'], '/', stats['total_free_hard'], ')')
    print('')
    print('Open:', stats['total_open'])
    print('')
    print('Today:')
    print('  Easy:', stats['today_easy'])
    print('  Medium:', stats['today_medium'])
    print('  Hard:', stats['today_hard'])

