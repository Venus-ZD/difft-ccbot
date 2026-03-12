import json
import logging

import websocket
from difft.auth import Authenticator
from difft import constants

from . import config as _config

PROD_DOMAIN = "openapi.difft.org"


class CCBotListener:
    def __init__(self, appid: str = None, secret: str = None, bot_id: str = None, domain: str = PROD_DOMAIN,
                 pass_unmentioned: bool = False):
        """
        Listen for incoming messages via WebSocket.
        Credentials loaded from env vars or ~/.ccbot/config.json if not provided.

        If pass_unmentioned=True, group messages where the bot is NOT @-mentioned
        are still passed to the handler with msg["_mentioned"] = False.
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
        self._secret = creds["secret"]
        self._bot_id = creds["bot_id"]
        self._domain = domain
        self._pass_unmentioned = pass_unmentioned
        self._handler = None

    def handler(self, fn):
        """Register a message handler function."""
        self._handler = fn

    def start(self):
        """Start listening. Blocks until connection is closed."""
        auth = Authenticator(appid=self._appid, key=self._secret.encode("utf-8"))
        data = auth.build_data("GET", "/v1/websocket", {}, {}, None)
        sig = auth.sign(data)

        headers = [
            f"{constants.HEADER_NAME_APPID}:{self._appid}",
            f"{constants.HEADER_NAME_TIMESTAMP}:{sig.timestamp}",
            f"{constants.HEADER_NAME_NONCE}:{sig.nonce}",
            f"{constants.HEADER_NAME_ALGORITHM}:{sig.algorithm}",
            f"{constants.HEADER_NAME_SIGNEDHEADERS}:",
            f"{constants.HEADER_NAME_SIGNATURE}:{sig.signature}",
        ]

        ws = websocket.WebSocketApp(
            f"wss://{self._domain}/v1/websocket",
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        ws.run_forever(ping_interval=30)

    def _on_open(self, ws):
        logging.info("[ccbot] websocket connected")
        ws.send('{"cmd":"fetch"}')

    def _on_message(self, ws, raw):
        try:
            data = json.loads(raw)
            for item in data.get("messages", []):
                msg = item.get("data", {})
                src = msg.get("src")
                msg_type = msg.get("type")
                body = msg.get("msg", {}).get("body", "")

                # ignore bot's own messages
                if src == self._bot_id:
                    continue

                # for group messages, check if bot is @-mentioned
                dest = msg.get("dest", {})
                if dest.get("type") == "GROUP":
                    at_persons = msg.get("atPersons") or msg.get("msg", {}).get("atPersons") or []
                    mentioned = self._bot_id in at_persons
                    msg["_mentioned"] = mentioned
                    if not mentioned and not self._pass_unmentioned:
                        continue
                else:
                    msg["_mentioned"] = True

                # ignore non-TEXT types
                if msg_type != "TEXT":
                    continue

                attachment = msg.get("msg", {}).get("attachment")
                has_text = body and body != "[Unsupported message type]"

                # skip if neither text nor attachment
                if not has_text and not attachment:
                    continue

                if self._handler:
                    try:
                        self._handler(msg)
                    except Exception as e:
                        logging.error(f"[ccbot] handler error: {e}")
        except Exception as e:
            logging.error(f"[ccbot] on_message error: {e}")

        ws.send('{"cmd":"fetch"}')

    def _on_error(self, ws, error):
        logging.error(f"[ccbot] websocket error: {error}")

    def _on_close(self, ws, code, msg):
        logging.info(f"[ccbot] websocket closed: {code} {msg}")
