import io
import logging
import sys
import traceback
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
    # await context.send(e)

@bot.event
async def on_error(e, *args, **kwargs):
    from . import reporting
    await Bot.on_error(bot, e, *args, **kwargs)
    string = io.StringIO()
    traceback.print_exc(file=string)
    reporting.log('Error', f'```\n{string.getvalue()}```')

from . import proxy, feed, reporting

def setup_logger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s:\n%(message)s\n')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler = reporting.WebhookHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

def run():
    setup_logger()
    proxy.init(bot)
    feed.init(bot)
    bot.run(config.get('discord_token'))
