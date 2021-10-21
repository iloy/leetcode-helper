
from typing import *

cache_enable: bool = True
cache_data: Dict[str, Any] = {}
cache_hit: int = 0
cache_miss: int = 0

def cache_initialize(enable: bool = True) -> None:
    global cache_enable
    cache_enable = enable

def cache_terminate() -> None:
    print(f'cache statistics: hit: {cache_hit}, miss: {cache_miss}')

def cache_add(key: str, value: Any) -> None:
    if not cache_enable:
        return

    cache_data[key] = value

def cache_get(key: str) -> Any:
    if not cache_enable:
        return None

    if key not in cache_data:
        global cache_miss
        cache_miss += 1
        return None
    global cache_hit
    cache_hit += 1
    return cache_data[key]

def cache_invalidate(key: Optional[str] = None) -> None:
    if not cache_enable:
        return

    global cache_data
    if key is None:
        cache_data.clear()
    elif key in cache_data:
        del cache_data[key]

def cache_keys() -> List[str]:
    if not cache_enable:
        return []

    return list(cache_data.keys())

if __name__ == '__main__':

    cache_initialize()

    print(cache_keys())
    assert cache_get('k1') == None
    cache_add('k2', 'd2')
    assert cache_get('k2') == 'd2'
    print(cache_keys())
    cache_add('k3', 'd3')
    assert cache_get('k3') == 'd3'
    print(cache_keys())
    cache_invalidate('k3')
    assert cache_get('k3') is None
    assert cache_get('k2') == 'd2'
    print(cache_keys())
    cache_invalidate()
    assert cache_get('k2') is None
    print(cache_keys())

    cache_terminate()

