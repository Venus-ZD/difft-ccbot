# venus-claude-cc-bot

A Difft messaging bot that gives Venus Protocol team members access to Claude Code through the Difft app — no Terminal required.

## What it does

Team members send messages to the bot via Difft (DM or group @ mention). The bot forwards the request to Claude Code and replies with the response. Everyone on the team gets Claude Code access through the app they already use.

```
User on Difft → @VenusAlertBot "help me write a SQL query"
                     ↓
              Claude Code processes
                     ↓
Bot replies in Difft with the answer
```

## Package: `ccbot`

The `ccbot` Python package handles all Difft communication — sending, receiving, and image uploads.

### Installation

```bash
pip install -e /path/to/ccbot
```

### Setup

```bash
ccbot setup
```

Saves credentials to `~/.ccbot/config.json`. Or use env vars:

```bash
export CCBOT_APPID=your_app_id
export CCBOT_SECRET=your_app_secret
export CCBOT_BOT_ID=your_bot_id
```

### Sending messages

```python
import ccbot

# Text
ccbot.send("job done", to="group_id")
ccbot.send("job done", to="+user_id")

# Card (supports markdown)
ccbot.send("Venus TVL dropped 10%", to="group_id", title="Alert")

# Multiple targets
ccbot.send("done", to=["group_id", "+user_id"])

# Upload image and embed in card
url = ccbot.upload_pic("./chart.png")
ccbot.send(f"![chart]({url})", to="group_id", title="Weekly Report")
```

### Receiving messages

```python
import ccbot

def handler(msg):
    src = msg["src"]                          # sender ID
    body = msg["msg"]["body"]                 # message text
    dest = msg["dest"]
    group_id = dest.get("groupID") if dest["type"] == "GROUP" else None
    reply_to = group_id if group_id else src

    ccbot.send(f"Got it: {body}", to=reply_to)

ccbot.listen(handler)  # blocking, reconnects automatically
```

**Inbound filter rules:**
- Group messages: only triggers when bot is @-mentioned
- DM: always triggers
- Skips bot's own messages, empty bodies, unsupported attachment types

### CLI

```bash
ccbot "job done" --to GROUP_ID
ccbot "TVL dropped" --to GROUP_ID --title "Alert"
ccbot listen          # print incoming messages to stdout
ccbot setup
```

## Running the Claude Code service

`cc_bot_service.py` is the main service script. It listens for Difft messages and routes them to Claude Code:

```bash
python3 scripts/cc_bot_service.py
```

For production, run as a systemd service (see Step 4 in project notes).

## Credentials

- **Bot ID:** `+29577` (VenusAlertBot)
- **App ID:** `779f22315993380f8bf8`
- **Server IP:** `18.171.3.108` (AWS EU West 2, whitelisted in Difft)
- **WebSocket:** must be enabled in Difft admin console for the App ID

## License

MIT
