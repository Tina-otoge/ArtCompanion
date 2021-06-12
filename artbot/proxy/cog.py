import logging
import inspect
import discord
from discord.ext import commands

from artbot import services
from .proxy import Proxy

log = logging.getLogger(__name__)

class ProxyCog(commands.Cog):
    def __init__(self, bot : commands.Bot, services=[]):
        self.bot = bot

    @commands.command()
    async def register(self, context: commands.Context, service, *args):
        service : Proxy = services.get(Proxy, service, init=True)
        if not service:
            return
        users = service.get_users()
        users[str(context.author.id)] = args
        service.save_users(users)
        await context.send('saved')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for service in services.all(Proxy, init=True):
            match = service.extract(message.content)
            if not match:
                # ignoring
                continue
            log.info(f'{service} content detected, attaching triggers...')
            for emoji in service.triggers:
                await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
        user = payload.member
        if user == self.bot.user:
            return
        emoji = str(payload.emoji)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        content = message.content
        for service in services.all(Proxy, init=True):
            trigger = service.triggers.get(emoji)
            if not trigger:
                continue
            match = service.extract(content)
            if not match:
                continue
            author = service.login(user)
            if not author:
                continue
            function = getattr(service, trigger, None)
            if function:
                log.info(f'Proxying action to {function} on behalf of {user}')
                function(author, match)
