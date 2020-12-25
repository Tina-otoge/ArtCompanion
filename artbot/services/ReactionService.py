import inspect
import re
import discord
from discord.ext import commands

from .. import bot, data

class Service:
    def __init__(self, extracters=[], triggers={}, data_key=None, authenticator=None):
        self.extracters = [
            re.compile(x) if isinstance(x, str) else x
            for x in extracters
        ]
        self.triggers = triggers
        self.data_key = data_key
        self.authenticator = authenticator

    def extract(self, s: str):
        for regex in self.extracters:
            matches = re.search(regex, s)
            if matches:
                return matches.group(1)

    def login(self, user: discord.User):
        credentials = self.get_users().get(str(user.id))
        if not credentials or not self.authenticator:
            return credentials
        return self.authenticator(credentials)

    def get_users(self):
        return data.get(self.data_key, {})

    def save_users(self, users):
        data.set(self.data_key, users)


class ServicesHandler(commands.Cog):
    def __init__(self, bot, services=[]):
        self.bot = bot
        self.services = {}
        for x in services:
            self.attach(x)

    @staticmethod
    def get_service_name(service: Service):
        return service.__class__.__name__.lower()

    def get_service(self, name: str):
        return self.services.get(name.lower())

    def attach(self, service: Service):
        if inspect.isclass(service):
            service = service()
        self.services[self.get_service_name(service)] = service

    def dettach(self, service: Service):
        del self.services[self.get_service_name(service)]

    @commands.command()
    async def register(self, context: commands.Context, service, *args):
        service = self.get_service(service)
        if not service:
            return
        users = service.get_users()
        users[str(context.author.id)] = args
        service.save_users(users)
        await context.send('saved')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        for service in self.services.values():
            match = service.extract(message.content)
            if not match:
                # ignoring
                continue
            print('{} content detected, attaching triggers...'.format(service))
            for emoji in service.triggers:
                await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.bot.user:
            return
        for service in self.services.values():
            trigger = service.triggers.get(reaction.emoji)
            if not trigger:
                continue
            match = service.extract(reaction.message.content)
            if not match:
                continue
            author = service.login(user)
            if not author:
                continue
            function = getattr(service, trigger, None)
            if function:
                print('Proxying action to {} on behalf of {}'.format(
                    function, user,
                ))
                function(author, match)
