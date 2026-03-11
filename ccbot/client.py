import time
from typing import Union

import requests

from .auth import Authenticator
from . import config as _config

API_URL = "https://openapi.difft.org/v1/messages"


def _detect_type(target: str) -> str:
    """Auto-detect target type: starts with '+' → USER, otherwise → GROUP."""
    return "USER" if target.startswith("+") else "GROUP"


def _build_payload(bot_id: str, target: str, text: str, title: str = None) -> dict:
    target_type = _detect_type(target)
    dest = {
        "wuid": [target] if target_type == "USER" else [],
        "groupID": target if target_type == "GROUP" else "",
        "type": target_type,
    }
    now_ms = int(time.time() * 1000)

    if title:
        return {
            "version": 1,
            "type": "CARD",
            "src": bot_id,
            "dest": dest,
            "timestamp": now_ms,
            "msg": {"body": "", "atPersons": []},
            "mentions": [],
            "card": {"appid": None, "title": title, "content": text},
        }
    else:
        return {
            "version": 1,
            "type": "TEXT",
            "src": bot_id,
            "dest": dest,
            "timestamp": now_ms,
            "msg": {"body": text, "atPersons": []},
            "mentions": [],
        }


class CCBot:
    def __init__(self, appid: str = None, secret: str = None, bot_id: str = None):
        """
        Initialize CCBot with credentials.
        If not provided, loads from env vars or ~/.ccbot/config.json.
        """
        if appid and secret and bot_id:
            creds = {"appid": appid, "secret": secret, "bot_id": bot_id}
        else:
            creds = _config.load()
            if appid:
                creds["appid"] = appid
            if secret:
                creds["secret"] = secret
            if bot_id:
                creds["bot_id"] = bot_id

        self._appid = creds["appid"]
        self._bot_id = creds["bot_id"]
        self._auth = Authenticator(appid=self._appid, key=creds["secret"].encode())

    def send(self, text: str, to: Union[str, list], title: str = None) -> None:
        """
        Send a message to one or more targets.

        Args:
            text:  Message body.
            to:    Target ID(s). String or list. Starts with '+' → USER, else → GROUP.
                   Can mix group IDs and user IDs in the same list.
            title: Optional. If set, sends as CARD type with this title.

        Raises:
            RuntimeError: If any send fails.
        """
        targets = [to] if isinstance(to, str) else list(to)
        errors = []

        for target in targets:
            payload = _build_payload(self._bot_id, target, text, title)
            if title:
                payload["card"]["appid"] = self._appid
            try:
                r = requests.post(API_URL, auth=self._auth, json=payload, timeout=10)
                data = r.json()
                if data.get("status") != 0:
                    errors.append(f"{target}: {data.get('reason', r.text)}")
            except Exception as e:
                errors.append(f"{target}: {e}")

        if errors:
            raise RuntimeError("ccbot send failed:\n" + "\n".join(errors))
