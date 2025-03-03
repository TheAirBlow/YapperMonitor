import discord
import asyncio
import logging
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
MONITORED_USERS = set(map(int, os.getenv("MONITORED_USERS", "").split(",")))

COUNTER_FILE = "/data/counter.txt"

counter = 0
previous_counter = 0
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        previous_counter = int(f.read().strip())

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
logger = logging.getLogger('discord')
lock = asyncio.Lock()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global counter, previous_counter

    if message.author.bot:
        return

    if message.guild.id != GUILD_ID:
        return

    async with lock:
        if message.author.id in MONITORED_USERS:
            counter += 1
        else:
            if counter > previous_counter:
                users = ''.join(map(lambda x: f" <@{x}>", MONITORED_USERS))
                await message.channel.send(f"{users} yapping streak is now {counter} messages")
                with open(COUNTER_FILE, "w") as f:
                    f.write(str(counter))
                previous_counter = counter
            counter = 0

bot.run(TOKEN)