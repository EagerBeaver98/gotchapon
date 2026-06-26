import json
import twitchio
import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO)

class Gotchapon(twitchio.Client):
    def __init__(self, config):
        super().__init__(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            bot_id=str(config["bot_id"])
        )
        self.owner_id=str(config["owner_id"])
        print(f"Initializing bot {config["bot_username"]} with channel: {config["twitch_channel"]}")

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        await self.add_token(payload.access_token, payload.refresh_token)

        chat_payload = twitchio.eventsub.ChatMessageSubscription(
            broadcaster_user_id=self.owner_id,
            user_id=self.bot_id
        )

        redeem_payload = twitchio.eventsub.ChannelPointsRewardAddSubscription(
            broadcaster_user_id=self.owner_id,
            user_id=self.bot_id
        )
        # subscribe_websocket opens a WebSocket connection to Twitch EventSub.
        try: 
            await self.subscribe_websocket(payload=chat_payload, as_bot=True)
            print("Chat Message EventSub subscription successful")
        except twitchio.HTTPException as e:
            print(f"Status: {e.status}")
            print(f"Details: {e.extra.get('message')}")

        try:
            await self.subscribe_websocket(payload=redeem_payload, as_bot=True)
            print("Channel Point Redeem EventSub successful")
        except twitchio.HTTPException as e:
            print(f"Status: {e.status}")
            print(f"Details: {e.extra.get('message')}")
        
    async def event_message(self, payload: twitchio.ChatMessage):
        print("Chat recieved")

    
    async def event_custom_redemption_add(self, payload: twitchio.ChannelPointsRedemptionAdd):
        print("channel points redeemed")

async def main():
    print("Starting Gotchapon Machine")
    with open("config.json") as f:
        config = json.load(f)

    bot = Gotchapon(config)
    await bot.start()

    
if __name__ == "__main__":
    asyncio.run(main())