#!/usr/bin/env python3

import asyncio
from copy import deepcopy
from datetime import date, datetime
from typing import *

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn # type: ignore

from cache import *
from done import update_time_done
from history import get_history
from pick import pick_problem, StatusEnum, BillingEnum
from problem import get_problem, DifficultyEnum
from start import insert_time_start
from stats import load_stats

app = FastAPI()

templates = Jinja2Templates(directory="templates")

last_date_lock = asyncio.Lock()
last_date = str(date.today())

@app.on_event("startup")
async def startup_event() -> None:
    cache_initialize(True)

@app.on_event("shutdown")
def shutdown_event() -> None:
    cache_terminate()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request) -> Response:
    key = '/'
    d = cache_get(key)
    if d is not None:
        return cast(Response, d)

    ret = templates.TemplateResponse('index.html', {'request': request})
    cache_add(key, ret)
    return ret

@app.get('/history', response_class=HTMLResponse)
async def history(request: Request) -> Response:
    key = '/history'
    d = cache_get(key)
    if d is not None:
        return cast(Response, d)

    ret = templates.TemplateResponse('history.html', {'request': request})
    cache_add(key, ret)
    return ret

@app.get('/playground', response_class=HTMLResponse)
async def playground(request: Request) -> Response:
    key = '/playground'
    d = cache_get(key)
    if d is not None:
        return cast(Response, d)

    ret = templates.TemplateResponse('playground.html', {'request': request})
    cache_add(key, ret)
    return ret

class TodayOpen(BaseModel):
    no: int
    name: str
    acceptance: float
    difficulty: DifficultyEnum
    paidonly: bool
    weblink: str
    time_elapsed: str

class StatsResponse(BaseModel):
    total_easy: int
    total_medium: int
    total_hard: int

    solved_easy: int
    solved_medium: int
    solved_hard: int

    total_free_easy: int
    total_free_medium: int
    total_free_hard: int

    solved_free_easy: int
    solved_free_medium: int
    solved_free_hard: int

    today_easy: int
    today_medium: int
    today_hard: int

    total_open: List[TodayOpen]

@app.get('/api/stats', response_model=StatsResponse)
async def api_stats() -> Dict[str, Any]:
    key = '/api/stats'

    async with last_date_lock:
        today = str(date.today())
        global last_date
        if last_date != today:
            last_date = today
            cache_invalidate(key)

    stats = cache_get(key)
    if stats is not None:
        pass
    else:
        stats = load_stats()
        cache_add(key, stats)
    stats = deepcopy(stats)

    total_open = []
    for no, time_start in stats['total_open']:
        now = datetime.now()
        delta = now - datetime.fromisoformat(time_start)
        problem = get_problem(no)
        if problem is not None:
            total_open.append({
                'no': problem.no,
                'name': problem.name,
                'acceptance': problem.acceptance,
                'difficulty': problem.difficulty,
                'paidonly': problem.paidonly,
                'weblink': problem.weblink,
                'time_elapsed': delta.days * 60 * 60 * 24 + delta.seconds,
            })
    stats['total_open'] = total_open
    return cast(Dict[str, Any], stats)

class PickRequest(BaseModel):
    target_difficulties: List[DifficultyEnum]
    target_status: List[StatusEnum]
    target_billing: List[BillingEnum]

class PickResponse(BaseModel):
    no: int
    name: str
    acceptance: float
    difficulty: DifficultyEnum
    paidonly: bool
    weblink: str
    solved: bool
    time_elapsed: str

@app.post('/api/pick', response_model=PickResponse)
async def api_pick(request: PickRequest) -> Union[Response, Dict[str, Any]]:
    try:
        problem, solved, time_elapsed = pick_problem(
                request.target_difficulties,
                request.target_status,
                request.target_billing,
                )
        if not problem:
            return JSONResponse(content = {})

        return {
            'no': problem.no,
            'name': problem.name,
            'acceptance': problem.acceptance,
            'difficulty': problem.difficulty,
            'paidonly': problem.paidonly,
            'weblink': problem.weblink,
            'solved': solved,
            'time_elapsed': time_elapsed,
        }
    except:
        return JSONResponse(content = {})

class MarkStartRequest(BaseModel):
    no: int
    solved: bool

class MarkStartResponse(BaseModel):
    time_start: str

@app.post('/api/mark_start', response_model=MarkStartResponse)
async def api_mark_start(request: MarkStartRequest) -> Union[Response, Dict[str, str]]:
    try:
        time_start = insert_time_start(request.no, request.solved)

        cache_invalidate('/api/stats')
        cache_invalidate('/api/history')

        return {
            'time_start': time_start,
        }
    except:
        return JSONResponse(content = {})

class MarkDoneRequest(BaseModel):
    no: int

class MarkDoneResponse(BaseModel):
    time_start: str
    time_done: str
    time_elapsed: str

@app.post('/api/mark_done', response_model=MarkDoneResponse)
async def api_mark_done(request: MarkDoneRequest) -> Union[Response, Dict[str, str]]:
    try:
        time_start, time_done, time_elapsed = update_time_done(request.no)

        cache_invalidate('/api/stats')
        cache_invalidate('/api/history')

        return {
            'time_start': time_start,
            'time_done': time_done,
            'time_elapsed': time_elapsed,
        }
    except:
        return JSONResponse(content = {})

class HistoryResponse(BaseModel):
    no: int
    name: str
    acceptance: float
    difficulty: DifficultyEnum
    weblink: str
    time_start: str
    time_done: str
    time_elapsed: str

@app.get('/api/history', response_model=List[HistoryResponse])
async def api_history() -> Union[Response, List[Dict[str, Any]]]:
    key = '/api/history'
    d = cache_get(key)
    if d is not None:
        return cast(Union[Response, List[Dict[str, Any]]], d)

    history = get_history(reverse=True)
    content = []
    for h in history:
        p = h.problem
        content.append({
            'no': p.no,
            'name': p.name,
            'acceptance': p.acceptance,
            'difficulty': p.difficulty,
            'weblink': p.weblink,
            'time_start': h.time_start,
            'time_done': h.time_done,
            'time_elapsed': h.time_elapsed,
        })
    #return content # too slow
    ret = JSONResponse(content = content) # faster
    cache_add(key, ret)
    return ret
    #return JSONResponse(content = [] ) # fastest :$

'''
@app.post('/api/like')
async def api_like() -> None:
    no = request.form.get('no')
'''

if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8080)

