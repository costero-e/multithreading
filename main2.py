import asyncio
import aiohttp.web as web
import aiohttp
import logging
import json
from aiohttp.web import StreamResponse
import requests
import aiohttp
import asyncio
import time
import random
import itertools
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor

LOG = logging.getLogger(__name__)

async def beacon_request(session, url, data):
    async with session.post(url, json=data) as response:
        response_obj = await response.json()
        return response_obj


async def initialize(app):
    # Load static

    LOG.warning("Initialization done.")

async def requesting():
    data={"meta": {
            "apiVersion": "2.0"
        },
        "query":{ "requestParameters": {        },
            "filters": [
    {"id":"DOID:9256", "scope":"individual"}],
            "includeResultsetResponses": "HIT",
            "pagination": {
                "skip": 0,
                "limit": 10
            },
            "testMode": "false",
            "requestedGranularity": "record"
        }
    }
    my_timeout = aiohttp.ClientTimeout(
    total=60, # total timeout (time consists connection establishment for a new connection or waiting for a free connection from a pool if pool connection limits are exceeded) default value is 5 minutes, set to `None` or `0` for unlimited timeout
    sock_connect=10, # Maximal number of seconds for connecting to a peer for a new connection, not given from a pool. See also connect.
    sock_read=10 # Maximal number of seconds for reading a portion of data from a peer
)
    async with aiohttp.ClientSession(timeout=my_timeout) as session:
        url = 'https://beacon-spain.ega-archive.org/api/individuals'
        response_obj = await beacon_request(session, url, data)
        #LOG.warning(json.dumps(response_obj))
        return json.dumps(response_obj)
        #return web.Response(text=json.dumps(response_obj), status=200, content_type='application/json')

async def returning():
    await asyncio.sleep(0.1)
    response_obj = {'timeout': 'more than 0.1 seconds'}
    LOG.warning(json.dumps(response_obj))
    #return web.Response(text=json.dumps(response_obj), status=200, content_type='application/json')
    return response_obj

async def hello2():
    start_time = perf_counter()
    loop=asyncio.get_running_loop()
    tasks=[]
    with ThreadPoolExecutor() as pool:
        task = await loop.run_in_executor(pool, requesting)
        tasks.append(task)
    with ThreadPoolExecutor() as pool:
        task = await loop.run_in_executor(pool, returning)
        tasks.append(task)
    LOG.warning(tasks)
    #LOG.warning([(t.get_name(), t._state) for t in tasks])
    for task in itertools.islice(asyncio.as_completed(tasks), 2):
        return await task
    

async def bye(request):
    await asyncio.sleep(10)
    response_obj = {'status': 'bye'}
    return web.Response(text=json.dumps(response_obj), status=200, content_type='application/json')


async def apitry():
    app = web.Application()
    app.on_startup.append(initialize)
    app.add_routes([web.get('/', hello2)])
    app.add_routes([web.get('/bye', bye)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5050)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(apitry())