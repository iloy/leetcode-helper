
from datetime import datetime, timedelta
import gc
from string import Template
import sys
from typing import *

class DeltaTemplate(Template):
    delimiter = "%"

FMT = '%Y-%m-%d %H:%M:%S'

def strfdelta(start: str, end: str, fmt: str = '%H:%M:%S') -> str:
    tdelta = datetime.strptime(end, FMT) - datetime.strptime(start, FMT)

    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    hours += tdelta.days * 24
    d = {}
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def sizeof(input_obj: Any) -> int:
    memory_size = 0
    ids = set()
    objects = [input_obj]
    while objects:
        new = []
        for obj in objects:
            if id(obj) not in ids:
                ids.add(id(obj))
                memory_size += sys.getsizeof(obj)
                new.append(obj)
        objects = gc.get_referents(*new)
    return memory_size

