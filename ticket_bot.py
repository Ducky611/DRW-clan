"""
Ticket Tool Welcome Bot — Render-ready
Posts a custom message + image whenever Ticket Tool opens a new ticket.

Token is NEVER in this file:
  - On Render: set a DISCORD_TOKEN environment variable in the dashboard
  - Locally: put it in token.txt (gitignored)

Includes a tiny keep-alive web server that auto-starts ONLY on Render
(free Web Services need an open port). Locally it does nothing.
"""

import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord

# ============ EDIT THESE ============
TICKET_PREFIX = "ticket-"   # Ticket Tool channels start with this (change if you customized the name format)
WELCOME_MESSAGE = "Hey {user}! Thanks for opening a ticket — describe your issue and support will be with you shortly. 🎫"
IMAGE_PATH = "welcome.png"  # image file committed in the repo, same folder as this script
DELAY_SECONDS = 2           # small wait so Ticket Tool finishes posting its own panel first

# Tickets created in these categories are IGNORED (no welcome message)
IGNORED_CATEGORY_IDS = {
    1529126664674607203,
    1529668023982751794,
}
# ====================================


def get_token():
    """Load the bot token without ever hardcoding it in the source."""
    # 1) Environment variable (this is what Render uses)
    token = os.getenv("DISCORD_TOKEN")
    if token and token.strip():
        return token.strip()

    # 2) Local token.txt next to this script (gitignored, for running on your PC)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            token = f.read().strip()
        if token:
            return token

    raise SystemExit(
        "❌ No token found!\n"
        "On Render: add DISCORD_TOKEN in the Environment tab.\n"
        "Locally: create token.txt next to this script with ONLY your token inside."
    )


def start_keepalive_server():
    """Render free Web Services must bind a port. Starts only if PORT is set (Render sets it)."""
    port = os.getenv("PORT")
    if not port:
        return  # running locally — no server needed

    class Ping(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is alive!")

        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass  # keep Render logs clean

    server = HTTPServer(("0.0.0.0", int(port)), Ping)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"🌐 Keep-alive server running on port {port}")


intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} — watching for new tickets ({TICKET_PREFIX}*)")


@client.event
async def on_guild_channel_create(channel):
    # Only care about text channels that look like tickets
    if not isinstance(channel, discord.TextChannel):
        return
    if not channel.name.lower().startswith(TICKET_PREFIX.lower()):
        return
    if channel.category_id in IGNORED_CATEGORY_IDS:
        print(f"⏭️ Skipping #{channel.name} — ignored category.")
        return

    # Give Ticket Tool a moment to set permissions + post its own message
    await asyncio.sleep(DELAY_SECONDS)

    # Re-fetch the channel so we see the final permission overwrites
    try:
        channel = await client.fetch_channel(channel.id)
    except discord.HTTPException:
        pass

    # Check again after re-fetch, in case Ticket Tool moved it into an ignored category
    if channel.category_id in IGNORED_CATEGORY_IDS:
        print(f"⏭️ Skipping #{channel.name} — ignored category.")
        return

    # Find who opened the ticket (Ticket Tool adds them as a member overwrite)
    opener = None
    for target in channel.overwrites:
        if isinstance(target, discord.Member) and not target.bot:
            opener = target
            break

    text = WELCOME_MESSAGE.replace("{user}", opener.mention if opener else "there")

    try:
        if os.path.exists(IMAGE_PATH):
            await channel.send(text, file=discord.File(IMAGE_PATH))
        else:
            print(f"⚠️ Image not found at '{IMAGE_PATH}' — sent text only.")
            await channel.send(text)
        print(f"📨 Posted welcome in #{channel.name}")
    except discord.Forbidden:
        print(f"❌ No permission to send in #{channel.name} — give the bot Admin, "
              f"or add its role to Ticket Tool's Support Team roles.")


start_keepalive_server()
client.run(get_token())
