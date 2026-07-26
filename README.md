# Ticket Tool Welcome Bot 🎫

Auto-posts a message + image whenever [Ticket Tool](https://tickettool.xyz) opens a new ticket, and pings the person who opened it.

## Deploy on Render

1. Push this folder to a GitHub repo.
2. On [Render](https://dashboard.render.com): **New → Blueprint** → pick this repo.
   Render reads `render.yaml` and sets everything up automatically.
3. When it asks for `DISCORD_TOKEN`, paste your bot token (Discord Developer Portal → Bot → Reset Token).
4. Click **Apply**. Watch the logs for `✅ Logged in as ...`

Runs as a **Background Worker** on the Starter plan (~$7/mo) — always online,
no sleeping, no keep-alive pinging needed.

## Customize

| What | How |
|---|---|
| **Image** | Replace `welcome.png` in the repo (keep the name), push — Render auto-redeploys |
| **Message** | Edit `WELCOME_MESSAGE` at the top of `ticket_bot.py` (`{user}` = ping the opener) |
| **Ticket name format** | Edit `TICKET_PREFIX` if your tickets aren't named `ticket-...` |

## Run locally instead

1. `pip install -r requirements.txt`
2. Create `token.txt` next to the script with only your token inside (it's gitignored)
3. `python ticket_bot.py`

## Discord setup

Invite the bot with **Administrator** (or add its role to Ticket Tool's Support Team
roles so it can see ticket channels). No privileged intents needed.
