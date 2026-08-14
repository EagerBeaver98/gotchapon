import json
import twitchio
import asyncio
import logging
import sys
import os
from rich.console import Console
from tkinter import messagebox, Tk
from rewards import RewardManager
from overlay import OverlayManager
from database import DatabaseManager
from errors import MissingRewardFolderException
from pathing import SOUNDS_DIR, CONFIG_PATH, SOUNDS_MANIFEST_PATH, BACKGROUND_PATH

logging.basicConfig(level=logging.INFO)

console = Console()

root = Tk()
root.withdraw()
class Gotchapon(twitchio.Client):
    def __init__(self, config):
        super().__init__(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            bot_id=str(config["bot_id"])
        )
        self.config = config
        self.owner_id=str(config["owner_id"])
        self.redeem_id = config["redeem_id"]
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
            console.print("[blue]Redeeming Gotchapon")
            redeemed_reward = self.Rewards.redeem_roulette()
            if redeemed_reward == None:
                console.print("[red]No rewards in folders. Please check rewards folder and ensure images have been added to the sub folders")
            else:    
                previous_rewards = self.Database.get_rewards(payload.chatter.id)
                self.Database.new_entry({"chatter_name": payload.chatter.name, "chatter_id": payload.chatter.id, "reward_name": redeemed_reward["reward_name"], "reward_tier": redeemed_reward["reward_tier"], "reward_path": redeemed_reward["reward_path"]})
                print(f"Reward redeemed {redeemed_reward["reward_name"]}")

                reward= {"name": redeemed_reward["reward_name"], "path": redeemed_reward["reward_path"], "chatter": payload.chatter.name, "previous_rewards": previous_rewards}

                await self.RedeemOverlay.redemption_trigger(rewardetails=reward)


    
    async def event_custom_redemption_add(self, payload: twitchio.ChannelPointsRedemptionAdd):
        print("channel points redeemed")
        if str(payload.reward.id) == self.redeem_id:
            console.print("[blue]Redeeming Gotchapon")
            redeemed_reward = self.Rewards.redeem_roulette()
            if redeemed_reward == None:
                print("No rewards in folders. Please check rewards folder and ensure images have been added to the sub folders")
            else:    
                previous_rewards = self.Database.get_rewards(payload.user.id)
                self.Database.new_entry({"chatter_name": payload.user.name, "chatter_id": payload.user.id, "reward_name": redeemed_reward["reward_name"], "reward_tier": redeemed_reward["reward_tier"], "reward_path": redeemed_reward["reward_path"]})
                print(f"Reward redeemed {redeemed_reward["reward_name"]}")

                reward= {"name": redeemed_reward["reward_name"], "path": redeemed_reward["reward_path"], "chatter": payload.user.name, "previous_rewards": previous_rewards}

                await self.RedeemOverlay.redemption_trigger(rewardetails=reward)


def folder_setup():
    rewards = RewardManager()
    try:
        reward_folders = rewards.get_reward_tiers()
    except MissingRewardFolderException as e:
        messagebox.showerror("Gotchapon - Reward Folder Error", str(e))
        sys.exit(str(e))
    if reward_folders == None:
        messagebox.showerror("Gotchapon - Rewards Missing", "No files in rewards folders. Add at least 1 reward image to a tier folder (ex. ./display/rewards/50/image.png)")
        sys.exit("No files in rewards folders. Add at least 1 reward image to a tier folder (ex. ./display/rewards/50/image.png)")
    if BACKGROUND_PATH == None:
        messagebox.showerror("Gotchapon - Background Image Missing", "Make sure to add a background image to the display folder")
        sys.exit("Make sure to add a background image to the display folder")
    if not CONFIG_PATH.is_file():
        with open(CONFIG_PATH, "w") as f:
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
                "redeem_id": "ID of redeem event in Twitch",
                "font-color": "black",
                "font-family": "Name of .ttf file in display folder",
                "font-shadow-color": "white" 
                }, f)
        print("Generated config file. Please edit config.json and run the app again")
        messagebox.showerror("Gotchapon - Config Error", "Generated config file. Please edit config.json and run the app again")
        sys.exit("Generated config file. Please edit config.json and run the app again")
    else:
        print("Config file detected")

    if not SOUNDS_DIR.exists():
        SOUNDS_DIR.mkdir()
        messagebox.showerror("Gotchapon - Sounds Folder Setup", "Sounds folder created. Enter in your sounds for the redemption event. Be sure to name them:\ncoin\ncrank\nrumble\nopen\ncelebrate\nFile type does not matter")
        sys.exit("Sounds folder created. Enter in your sounds for the redemption event. Be sure to name them:\ncoin\ncrank\nrumble\nopen\ncelebrate\nFile type does not matter")
    else :
        sound_list = list(os.listdir(SOUNDS_DIR))
        sound_dir = {}
        for sound in sound_list:
            stripped_name = sound.split(".")[0]
            sound_dir[stripped_name] = sound
        with open (SOUNDS_MANIFEST_PATH, "w") as f:
            json.dump(sound_dir, f)    

async def redeem_subscription(client, redeem_payload): 
    try:
        await client.subscribe_websocket(payload=redeem_payload, as_bot=True)
        console.print("[green]Channel Point Redeem EventSub successful")
    except twitchio.HTTPException as e:
        print(f"Status: {e.status}")
        print(f"Details: {e.extra.get('message')}")

async def chat_subscription(client, chat_payload): 
    try: 
        await client.subscribe_websocket(payload=chat_payload, as_bot=True)
        console.print("[green]Chat Message EventSub subscription successful")
    except twitchio.HTTPException as e:
        print(f"Status: {e.status}")
        print(f"Details: {e.extra.get('message')}")


async def main():
    console.print("[green]Starting Gotchapon Machine")
    print("Checking for setup files")
    bot = None
    try:
        folder_setup()
    except Exception as e:
        messagebox.showerror("Error while creating setup files", str(e))
        sys.exit(f"Error while creating setup files {e}")
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    except Exception as e:
        messagebox.showerror("Error Reading Config.json", str(e))
        console.print(f"[red bold]Error Reading Config.json - [white /bold]{e}")
        sys.exit()
    try:
        bot = Gotchapon(config)
        async with bot:
            await bot.start()
    except Exception as e:
        messagebox.showerror("Error starting Bot", str(e))
        console.print(f"[red bold]Error starting Bot - [white /bold]{e}")
        sys.exit()
    finally:
        if bot is not None:
            bot.Database.close_database()
        

    
if __name__ == "__main__":
    asyncio.run(main())