import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".ccbot" / "config.json"
ENV_APPID = "CCBOT_APPID"
ENV_SECRET = "CCBOT_SECRET"
ENV_BOT_ID = "CCBOT_BOT_ID"


def load() -> dict:
    """Load credentials from env vars, then config file. Returns dict with appid, secret, bot_id."""
    appid = os.environ.get(ENV_APPID)
    secret = os.environ.get(ENV_SECRET)
    bot_id = os.environ.get(ENV_BOT_ID)

    if appid and secret and bot_id:
        return {"appid": appid, "secret": secret, "bot_id": bot_id}

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        appid = appid or data.get("appid")
        secret = secret or data.get("secret")
        bot_id = bot_id or data.get("bot_id")

    missing = [k for k, v in {"appid": appid, "secret": secret, "bot_id": bot_id}.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing ccbot credentials: {', '.join(missing)}.\n"
            f"Run `ccbot setup` or set env vars {ENV_APPID}, {ENV_SECRET}, {ENV_BOT_ID}."
        )

    return {"appid": appid, "secret": secret, "bot_id": bot_id}


def save(appid: str, secret: str, bot_id: str):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"appid": appid, "secret": secret, "bot_id": bot_id}, f, indent=2)
    print(f"Config saved to {CONFIG_PATH}")
