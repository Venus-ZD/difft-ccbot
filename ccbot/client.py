import uuid
from typing import Union

from difft.client import DifftClient
from difft.message import MessageRequestBuilder

from . import config as _config

PROD_HOST = "https://openapi.difft.org"


def _detect_type(target: str) -> str:
    """Auto-detect target type: starts with '+' → USER, otherwise → GROUP."""
    return "USER" if target.startswith("+") else "GROUP"


class CCBot:
    def __init__(self, appid: str = None, secret: str = None, bot_id: str = None, host: str = PROD_HOST):
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
        self._secret = creds["secret"]
        self._host = host
        self._client = DifftClient(self._appid, creds["secret"], host)

    def send(self, text: str, to: Union[str, list], title: str = None) -> None:
        """
        Send a message to one or more targets.

        Args:
            text:  Message body (plain text, or markdown when title is set).
            to:    Target ID(s). String or list. Starts with '+' → USER, else → GROUP.
            title: Optional. If set, sends as CARD with title as H3 heading above text.

        Raises:
            RuntimeError: If any send fails.
        """
        targets = [to] if isinstance(to, str) else list(to)
        errors = []

        for target in targets:
            builder = MessageRequestBuilder().sender(self._bot_id).timestamp_now()

            if _detect_type(target) == "USER":
                builder = builder.to_user([target])
            else:
                builder = builder.to_group(target)

            if title:
                content = f"### {title}\n\n{text}"
                builder = builder.card(self._appid, uuid.uuid4().hex[:16], content)
            else:
                builder = builder.message(text)

            try:
                result = self._client.send_message(builder.build(), raw_response=True)
                if result.get("status") != 0:
                    errors.append(f"{target}: {result.get('reason', result)}")
            except Exception as e:
                errors.append(f"{target}: {e}")

        if errors:
            raise RuntimeError("ccbot send failed:\n" + "\n".join(errors))

    def upload_pic(self, path: str) -> str:
        """Upload a local image and return its URL for embedding in card markdown."""
        return self._client.upload_pic(path)
