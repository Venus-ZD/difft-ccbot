from .client import CCBot
from .listener import CCBotListener

_default: CCBot = None
_default_listener: CCBotListener = None


def _get_default() -> CCBot:
    global _default
    if _default is None:
        _default = CCBot()
    return _default


def _get_default_listener() -> CCBotListener:
    global _default_listener
    if _default_listener is None:
        _default_listener = CCBotListener()
    return _default_listener


def send(text: str, to, title: str = None) -> None:
    """Send a message using the default bot (credentials from env or ~/.ccbot/config.json)."""
    _get_default().send(text, to=to, title=title)


def upload_pic(path: str) -> str:
    """Upload a local image and return its URL."""
    return _get_default().upload_pic(path)


def listen(handler) -> None:
    """Start listening for incoming messages. Blocks until disconnected."""
    listener = _get_default_listener()
    listener.handler(handler)
    listener.start()


__all__ = ["CCBot", "CCBotListener", "send", "upload_pic", "listen"]
