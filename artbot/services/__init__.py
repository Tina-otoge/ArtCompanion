import importlib

from .ReactionService import ServicesHandler

def init(bot):
    bot.add_cog(ServicesHandler(bot, services=[
        getattr(
            importlib.import_module('{}.{}'.format(__name__, module.lower())),
            module
        ) for module in ['Pixiv', 'Twitter']
    ]))
