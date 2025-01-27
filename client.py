import websockets
import asyncio
 

async def ws_client():
    print("Connected.")
    url = "ws://127.0.0.1:5700"
    async with websockets.connect(url) as ws:
        while True:
            firstitem = input("First item: ")
    
    
            seconditem = input("Second item: ")
            await ws.send(f"{firstitem}")
            await ws.send(f"{seconditem}")
    
            while True:
                msg = await ws.recv()
                print(msg)
 
asyncio.run(ws_client())