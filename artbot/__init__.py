import discord

from .storage import Storage

config = Storage('./config.json', save_on_read=True)
data = Storage()

bot = discord.Client()

bot.run(config.get('token'))

from . import services
