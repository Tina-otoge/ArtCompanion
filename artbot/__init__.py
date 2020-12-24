from discord.ext.commands import Bot

from .storage import Storage

config = Storage('./config.json', save_on_read=True)
data = Storage()

bot = Bot('!')

def run():
    bot.run(config.get('token'))

from . import services
