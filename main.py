import json
import twitchio
import asyncio
import logging
import os

logging.basicConfig(level=logging.info)

TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
OWNER_ID = os.getenv("OWNER_ID")
BOT_ID = os.getenv("BOT_ID")
class Gotchapon(twitchio.Client):
    def __init__(self):
        super().__init__(
            client_id=TWITCH_CLIENT_ID,
            client_secret=TWITCH_SECRET,
            owner_id=OWNER_ID,
            bot_id=BOT_ID,
            scopes=["channel:read:redemptions", "chat:read"]
        )
        print(f"Initializing bot with channel: {TWITCH_CHANNEL}")

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        await self.add_token(payload.access_token, payload.refresh_token)
        


    
    
    async def event_ready(self):
        
        users=await self.fetch_users(name=self.config["bot_username"])
        
        print(f"Logged in as | {users}")
        print("Ready to receive events!")



async def main():
    with open("config.json") as f:
        config = json.load(f)

    bot = Gotchapon(config)
    await bot.start()

    
if __name__ == "__main__":
    asyncio.run(main())