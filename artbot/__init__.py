import sys
from discord.ext.commands import Bot

from .storage import Storage

config = Storage('./config.json', save_on_read=True)
data = Storage()
bot = Bot('!')

@bot.event
async def on_ready():
    print('ready', bot.user)

@bot.event
async def on_command_error(context, e):
    print(e, file=sys.stderr)
    await context.send(e)

from . import services

def run():
    services.init(bot)
    bot.run(config.get('discord_token'))
