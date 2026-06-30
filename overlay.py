import asyncio
import websockets
import json


class OverlayManager():
    def __init__(self, jsonconfig):
        self.host = jsonconfig["obs_host"]
        self.obsport = jsonconfig["obs_port"]
        self.port = jsonconfig["overlay_port"]


    async def server(websocket):
