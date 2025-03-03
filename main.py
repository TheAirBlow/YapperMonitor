import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
MONITORED_USERS = set(map(int, os.getenv("MONITORED_USERS", "").split(",")))

COUNTER_FILE = "/data/counter.txt"

counter = 0
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        try:
            counter = int(f.read().strip())
        except:
            pass

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
lock = asyncio.Lock()

def save_counter(value):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global counter

    if message.author.bot:
        return

    if message.guild.id != GUILD_ID:
        return

    async with lock:
        previous_counter = counter

        if message.author.id in MONITORED_USERS:
            counter += 1
            save_counter(counter)

        else:
            if counter > previous_counter:
                await message.channel.send(f"{map(lambda x: f" <@{x}>", MONITORED_USERS)} yapping streak is now {counter} messages")
            counter = 0
            save_counter(counter)

bot.run(TOKEN)
