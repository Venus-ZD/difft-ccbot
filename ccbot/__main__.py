import argparse
import sys

from . import config as _config
from .client import CCBot


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


def main():
    parser = argparse.ArgumentParser(prog="ccbot")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("setup", help="Interactive credential setup")

    send_p = sub.add_parser("send", help="Send a message")
    send_p.add_argument("message", help="Message text")
    send_p.add_argument("--to", nargs="+", required=True, help="Target group ID(s) or user ID(s)")
    send_p.add_argument("--title", default=None, help="Optional card title (sends as CARD type)")

    # Allow: python3 -m ccbot "msg" --to GID (send as default subcommand)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] != "setup" and sys.argv[1] != "send":
        sys.argv.insert(1, "send")

    args = parser.parse_args()

    if args.cmd == "setup":
        cmd_setup(args)
    elif args.cmd == "send":
        cmd_send(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
