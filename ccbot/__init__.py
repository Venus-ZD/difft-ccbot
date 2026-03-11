from .client import CCBot

_default: CCBot = None


def _get_default() -> CCBot:
    global _default
    if _default is None:
        _default = CCBot()
    return _default


def send(text: str, to, title: str = None) -> None:
    """Send a message using the default bot (credentials from env or ~/.ccbot/config.json)."""
    _get_default().send(text, to=to, title=title)


__all__ = ["CCBot", "send"]
