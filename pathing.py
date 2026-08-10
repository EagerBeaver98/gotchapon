import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

DISPLAY_DIR = BASE_DIR / "display"
REWARDS_DIR = DISPLAY_DIR / "rewards"
SOUNDS_DIR = DISPLAY_DIR / "sounds"
SOUNDS_MANIFEST_PATH = DISPLAY_DIR / "soundsDir.json"
DISPLAY_CONFIG_PATH = DISPLAY_DIR / "displayconfig.json"

CONFIG_PATH = BASE_DIR / "config.json"
DATABASE_PATH = BASE_DIR / "redeems.db"
BACKGROUND_PATH = DISPLAY_DIR.glob("background*")