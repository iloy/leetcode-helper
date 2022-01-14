#!/usr/bin/env python3

import json
import subprocess
import sqlite3
import time
from typing import *

import requests

from database import DATABASE_FILENAME, vacuum
from problem import Problem

def get_call_result(command: str) -> str:
    s = subprocess.check_output(command,
            shell=True)
    return s.decode('utf-8')

def crawl() -> List[Problem]:
    total = None

    skip = 0
    limit = 50

    command = f'./graphql.sh {skip} {limit}'
    res = get_call_result(command)
    info = json.loads(res)

    total = info['data']['problemsetQuestionList']['total']
    #print(json.dumps(info, indent=4, sort_keys=True))


    questions = []

    skip = 0
    limit = 100
    for i in range((total + 99) // limit):
        print(i+1)
        time.sleep(1)
        skip = i * limit
        command = f'./graphql.sh {skip} {limit}'
        res = get_call_result(command)
        info = json.loads(res)
        for q in info['data']['problemsetQuestionList']['questions']:
            p = Problem(
                    q['frontendQuestionId'],
                    q['title'],
                    round(q['acRate'], 1),
                    q['difficulty'],
                    q['paidOnly'],
                    q['titleSlug'],
                    )
            questions.append(p)

    #print(questions)
    return questions

def insert(problems: List[Problem]) -> None:
    problems_list = []
    for p in problems:
        problems_list.append((p.no, p.name, p.acceptance, p.difficulty, p.paidonly, p.weblink))

    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()

    try:
        cur.execute('DELETE FROM problems')

        cur.executemany('INSERT INTO problems (id, title, acceptance, difficulty, plus, weblink) VALUES (?, ?, ?, ?, ?, ?)', problems_list)

        con.commit()
    finally:
        cur.close()
        con.close()

if __name__ == '__main__':

    get_call_result('sqlite3 leetcode.sqlite3 < schema')

    problems = crawl()
    insert(problems)
    vacuum()

    get_call_result('touch app.py')

