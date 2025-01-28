import websockets
import asyncio
import aiohttp
import json
import asyncio
import itertools
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
import logging


LOG = logging.getLogger(__name__)

async def beacon_request(session, url, data):
    async with session.post(url, json=data) as response:
        response_obj = await response.json()
        return response_obj

async def requesting(websocket):
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

async def returning(websocket):
    await asyncio.sleep(10)
    response_obj = {'timeout': 'more than 10 seconds'}
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
 
# Creating WebSocket server
async def ws_server(websocket):
    LOG.warning("WebSocket: Server Started.")
    try:

        firstitem = await websocket.recv()
        seconditem = await websocket.recv()

        # Prompt message when any of the field is missing
        if firstitem == "" or seconditem == "":
            LOG.warning("Not accepted.")


        LOG.warning(f"First: {firstitem}")
        LOG.warning(f"Second: {seconditem}")

        list_of_sockets=[]

        start_time = perf_counter()
        loop=asyncio.get_running_loop()
        tasks=[]
        with ThreadPoolExecutor() as pool:
            task = await loop.run_in_executor(pool, requesting, websocket)
            tasks.append(task)
        with ThreadPoolExecutor() as pool:
            task = await loop.run_in_executor(pool, returning, websocket)
            tasks.append(task)
        for task in itertools.islice(asyncio.as_completed(tasks), 2):
            response = await task
            list_of_sockets.append(response)
            await websocket.send(f"{list_of_sockets}")
            
 
    except websockets.ConnectionClosedError as e:
        LOG.warning(e)
 
 
async def main():
    async with websockets.serve(ws_server, "0.0.0.0", 3000):
        await asyncio.Future()
 
if __name__ == "__main__":
    asyncio.run(main())