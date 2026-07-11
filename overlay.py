import asyncio
import websockets
import json
import http.server
import functools
import os


class OverlayManager():
    def __init__(self, jsonconfig):
        self.host = jsonconfig["obs_host"]
        self.obsport = jsonconfig["obs_port"]
        self.wsport = jsonconfig["websocket_port"]
        self.port = jsonconfig["overlay_port"]
        self.clients = set()


    async def websocket_server(self, websocket):
        self.clients.add(websocket)
        
        try:
            async for _ in websocket:
                pass
        finally:
            self.clients.remove(websocket)

    async def redemption_trigger(self, rewardetails):
        if not self.clients:
            print("No overlay clients detected. Ensure OBS is active")
            return
        
        websockets.broadcast(self.clients, json.dumps(rewardetails))

    def http_server(self):
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler,
            directory="./overlay"
        )

        server = http.server.ThreadingHTTPServer((self.host, self.port), handler)
        print(f"Overlay server running at {self.host}:{self.port}")

        server.serve_forever()

    async def start(self):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, self.http_server)

        async with websockets.serve(self.websocket_server, self.host, self.wsport):
            await asyncio.Future()


async def test():
    with open("config.json") as f:
        config = json.load(f)
    
    overlay = OverlayManager(config)

    asyncio.create_task(overlay.start())

    await asyncio.sleep(5)
    await overlay.redemption_trigger(
        rewardetails={"name": "RewardTest", "path": "./rewards/75/example.png", "chatter": "Bob"}
    )            
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(test())
