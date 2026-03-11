# ccbot

Python SDK for sending messages via the [Difft](https://difft.org) messaging platform. Bring your own bot credentials.

## Installation

```bash
pip install ccbot
```

## Setup

Run the interactive setup once to save your credentials:

```bash
ccbot setup
```

This writes to `~/.ccbot/config.json`. Alternatively, use env vars:

```bash
export CCBOT_APPID=your_app_id
export CCBOT_SECRET=your_app_secret
export CCBOT_BOT_ID=your_bot_id
```

## Usage

### In a script

```python
from ccbot import send

# Send text to a group
send("job done", to="4c67045cb9d04cd4a48fe8ae9cde7b85")

# Send DM to a user
send("job done", to="+74189820376")

# Mix groups and users in one call
to_list = ["4c67045cb9d04cd4a48fe8ae9cde7b85", "+74189820376"]
send("job done", to=to_list)

# Send as card (with title)
send("Venus TVL dropped 10%", to=to_list, title="Alert")
```

Target type is auto-detected: IDs starting with `+` are treated as users (DM), others as groups.

### Explicit bot instance

```python
from ccbot import CCBot

bot = CCBot(appid="...", secret="...", bot_id="...")
bot.send("hello", to="group_id")
```

### CLI

```bash
# Send text
ccbot "job done" --to GROUP_ID

# Send to multiple targets
ccbot "job done" --to GROUP_ID +USER_ID

# Send as card
ccbot "TVL dropped 10%" --to GROUP_ID --title "Alert"

# Interactive setup
ccbot setup
```

### Cron pattern

```bash
python3 my_script.py \
  && ccbot "my_script: success" --to GROUP_ID \
  || ccbot "my_script: FAILED" --to GROUP_ID --title "ERROR"
```

## How to get your credentials

1. Register a bot app at [Difft Open Platform](https://openapi.difft.org)
2. Note your **App ID** and **App Secret**
3. Note your **Bot ID** (assigned when the bot is created)
4. Whitelist your server's outbound IP in the Difft developer console
5. Add your bot to the target group

## License

MIT
