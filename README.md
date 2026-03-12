# difft-ccbot

Python SDK for sending and receiving messages via the [Difft / CC](https://difft.org) messaging platform. Bring your own bot credentials.

## Installation

```bash
pip install -e git+https://github.com/Venus-ZD/difft-ccbot.git#egg=ccbot
```

Or clone and install locally:

```bash
git clone https://github.com/Venus-ZD/difft-ccbot.git
pip install -e ./difft-ccbot
```

## Setup

Run the interactive setup once to save your credentials:

```bash
ccbot setup
```

This writes to `~/.ccbot/config.json`. Or use env vars:

```bash
export CCBOT_APPID=your_app_id
export CCBOT_SECRET=your_app_secret
export CCBOT_BOT_ID=your_bot_id
```

## Sending messages

```python
import ccbot

# Text message to a group
ccbot.send("job done", to="group_id")

# DM to a user
ccbot.send("job done", to="+user_id")

# Multiple targets
ccbot.send("done", to=["group_id", "+user_id"])

# Card with markdown title
ccbot.send("TVL dropped 10%", to="group_id", title="Alert")

# Upload image and embed in card
url = ccbot.upload_pic("./chart.png")
ccbot.send(f"![chart]({url})", to="group_id", title="Weekly Report")
```

Target type is auto-detected: IDs starting with `+` → DM, others → group.

## Receiving messages

```python
import ccbot

def handler(msg):
    src = msg["src"]                    # sender ID
    body = msg["msg"]["body"]           # message text
    dest = msg["dest"]
    group_id = dest.get("groupID") if dest["type"] == "GROUP" else None
    reply_to = group_id if group_id else src

    ccbot.send(f"Got: {body}", to=reply_to)

ccbot.listen(handler)   # blocks, reconnects automatically
```

**Inbound filter rules:**
- Group messages: only triggers when bot is @-mentioned
- DM: always triggers
- Skips bot's own messages, empty bodies, and `[Unsupported message type]`

## Explicit bot instance

```python
from ccbot import CCBot, CCBotListener

bot = CCBot(appid="...", secret="...", bot_id="...")
bot.send("hello", to="group_id")

listener = CCBotListener(appid="...", secret="...", bot_id="...")
listener.handler(my_handler)
listener.start()
```

## CLI

```bash
ccbot "job done" --to GROUP_ID
ccbot "TVL dropped" --to GROUP_ID --title "Alert"
ccbot listen          # print incoming messages to stdout
ccbot setup
```

## Cron pattern

```bash
python3 my_script.py \
  && ccbot "my_script: success" --to GROUP_ID \
  || ccbot "my_script: FAILED" --to GROUP_ID --title "ERROR"
```

## Getting credentials

1. Register a bot app at the Difft Open Platform / Contact ccBot(10003)
2. Note your **App ID** and **App Secret**
3. Note your **Bot ID** (assigned when the bot is created)
4. Whitelist your server's outbound IP in the Difft developer console
5. Add your bot to the target group(s)
6. Enable WebSocket in the Difft admin console (required for receiving messages)

## Dependencies

- [`difft`](https://pypi.org/project/difft/) — official Difft Python SDK

## License

MIT
