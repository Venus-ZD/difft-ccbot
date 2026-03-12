import argparse
import sys

from . import config as _config
from .client import CCBot
from .listener import CCBotListener


def cmd_setup(args):
    print("ccbot setup — enter your Difft bot credentials")
    appid = input("App ID: ").strip()
    secret = input("App Secret: ").strip()
    bot_id = input("Bot ID (e.g. +29577): ").strip()
    _config.save(appid, secret, bot_id)


def cmd_send(args):
    bot = CCBot()
    to = args.to
    bot.send(args.message, to=to, title=args.title)
    print("sent")


def cmd_listen(args):
    import logging
    logging.basicConfig(level=logging.INFO)

    bot = CCBot()
    listener = CCBotListener()

    def handler(msg):
        src = msg.get("src")
        body = msg.get("msg", {}).get("body", "")
        dest = msg.get("dest", {})
        group_id = dest.get("groupID") if dest.get("type") == "GROUP" else None
        print(f"[{src}]: {body}")

    listener.handler(handler)
    print("Listening for messages... (Ctrl+C to stop)")
    listener.start()


def main():
    parser = argparse.ArgumentParser(prog="ccbot")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("setup", help="Interactive credential setup")

    send_p = sub.add_parser("send", help="Send a message")
    send_p.add_argument("message", help="Message text")
    send_p.add_argument("--to", nargs="+", required=True, help="Target group ID(s) or user ID(s)")
    send_p.add_argument("--title", default=None, help="Optional card title (sends as CARD type)")

    sub.add_parser("listen", help="Listen for incoming messages (prints to stdout)")

    # Allow: python3 -m ccbot "msg" --to GID (send as default subcommand)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in ("setup", "send", "listen"):
        sys.argv.insert(1, "send")

    args = parser.parse_args()

    if args.cmd == "setup":
        cmd_setup(args)
    elif args.cmd == "send":
        cmd_send(args)
    elif args.cmd == "listen":
        cmd_listen(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
