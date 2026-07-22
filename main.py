import json
import twitchio
import asyncio
import logging
import sys
import shutil
import os
from rewards import RewardManager
from overlay import OverlayManager
from database import DatabaseManager
from errors import MissingRewardFolderException

logging.basicConfig(level=logging.INFO)

class Gotchapon(twitchio.Client):
    def __init__(self, config):
        super().__init__(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            bot_id=str(config["bot_id"])
        )
        self.config = config
        self.owner_id=str(config["owner_id"])
        print(f"Initializing bot {config["bot_username"]} with channel: {config["twitch_channel"]}")
        self.RedeemOverlay = OverlayManager(jsonconfig=self.config)
        self.Rewards = RewardManager()
        self.Database = DatabaseManager()

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        await self.add_token(payload.access_token, payload.refresh_token)

        chat_payload = twitchio.eventsub.ChatMessageSubscription(
            broadcaster_user_id=self.owner_id,
            user_id=self.bot_id
        )

        redeem_payload = twitchio.eventsub.ChannelPointsRedeemAddSubscription(
            broadcaster_user_id=self.owner_id,
            user_id=self.bot_id
        )
        # subscribe_websocket opens a WebSocket connection to Twitch EventSub.
        await chat_subscription(self, chat_payload)

        await redeem_subscription(self, redeem_payload)


    async def setup_hook(self):
        
        if self.tokens:


            chat_payload = twitchio.eventsub.ChatMessageSubscription(
                broadcaster_user_id=self.owner_id,
                user_id=self.bot_id
            )

            redeem_payload = twitchio.eventsub.ChannelPointsRedeemAddSubscription(
                broadcaster_user_id=self.owner_id,
                user_id=self.bot_id
            )

            await chat_subscription(self, chat_payload)
            await redeem_subscription(self, redeem_payload)

            
        else:
            print(f"Oauth tokens have not been generated. Follow the authorization instructions in the README file to authorize your twitch account and bot account")
        
        asyncio.create_task(self.RedeemOverlay.start())



        
    async def event_message(self, payload: twitchio.ChatMessage):
        print(f"Chat message recieved {payload.text} from user {payload.chatter.name}")
        if payload.text.startswith("!redeemtest"):
            print("Redeeming Gotchapon")
            redeemed_reward = self.Rewards.redeem_roulette()
            if redeemed_reward == None:
                print("No rewards in folders. Please check rewards folder and ensure images have been added to the sub folders")
            else:    
                previous_rewards = self.Database.get_rewards(payload.chatter.id)
                self.Database.new_entry({"chatter_name": payload.chatter.name, "chatter_id": payload.chatter.id, "reward_name": redeemed_reward["reward_name"], "reward_tier": redeemed_reward["reward_tier"], "reward_path": redeemed_reward["reward_path"]})
                print(f"Reward redeemed {redeemed_reward["reward_name"]}")

                reward= {"name": redeemed_reward["reward_name"], "path": redeemed_reward["reward_path"], "chatter": payload.chatter.name, "previous_rewards": previous_rewards}

                await self.RedeemOverlay.redemption_trigger(rewardetails=reward)


    
    async def event_custom_redemption_add(self, payload: twitchio.ChannelPointsRedemptionAdd):
        print("channel points redeemed")



def folder_setup():
    rewards = RewardManager()
    try:
        reward_folders = rewards.get_reward_tiers()
    except MissingRewardFolderException as e:
        sys.exit(str(e))
    if reward_folders == None:
        sys.exit("No files in rewards folders. Add at least 1 reward image to a tier folder (ex. ./rewards/50/image.png)")

    if not os.path.isfile("./config.json"):
        with open("config.json", "w") as f:
            json.dump({
                "twitch_channel": "Your Twitch Channel",
                "owner_id": "Twitch Channel ID",
                "bot_username": "Twitch Bot Account Name",
                "bot_id": "Twitch Bot Account ID",
                "client_id": "Client ID from dev.twitch",
                "client_secret": "Client secret from dev.twitch",
                "obs_host": "localhost",
                "obs_port": 4455,
                "obs_password": "",
                "overlay_port": 8080,
                "overlay_duration_fade_in_gap": 2,
                "overlay_duration_hold": 8,
                "websocket_port": 8081,
                "redeem_id": "ID of redeem event in Twitch"
                }, f)
        print("Generated config file. Please edit config.json and run the app again")
        sys.exit("Generated config file. Please edit config.json and run the app again")
    else:
        print("Config file detected")

async def redeem_subscription(client, redeem_payload): 
    try:
        await client.subscribe_websocket(payload=redeem_payload, as_bot=True)
        print("Channel Point Redeem EventSub successful")
    except twitchio.HTTPException as e:
        print(f"Status: {e.status}")
        print(f"Details: {e.extra.get('message')}")

async def chat_subscription(client, chat_payload): 
    try: 
        await client.subscribe_websocket(payload=chat_payload, as_bot=True)
        print("Chat Message EventSub subscription successful")
    except twitchio.HTTPException as e:
        print(f"Status: {e.status}")
        print(f"Details: {e.extra.get('message')}")


async def main():
    print("Starting Gotchapon Machine")
    print("Checking for setup files")
    try:
        folder_setup()
    except Exception as e:
        sys.exit(f"Error while creating setup files {e}")
    with open("config.json") as f:
        config = json.load(f)

    bot = Gotchapon(config)
    async with bot:
        await bot.start()

    
if __name__ == "__main__":
    asyncio.run(main())