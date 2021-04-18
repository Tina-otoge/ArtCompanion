import asyncio
import io
import logging
import requests
import time
import discord
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook

from artbot import data, services, on_error
from .feed import Feed
from ..proxy.proxy import Proxy

log = logging.getLogger(__name__)

class FeedCog(commands.Cog):
    # Time between each post, avoid API limit
    WAIT_ITERATION_TIME = 2
    # Limit the amount of posts to post. WARNING: will update memory like if all posts were posted
    RESULTS_LIMIT = None
    # Limit of pics to post per post
    PICS_LIMIT = 10
    # Should the memory be ignored
    IGNORE_MEMORY = False
    # Time before each iteration
    LOOP_TIME = {'hours': 1}

    def __init__(self, bot: commands.Bot):
        self.bot : commands.Bot = bot
        self.loop.start()

    @commands.command()
    async def watch(self, context: commands.Context, service, *args):
        raise NotImplementedError

    @tasks.loop(**LOOP_TIME)
    async def loop(self):
        try:
            feeds = data.get('feeds', [])
            for index, rules in enumerate(feeds):
                log.debug(f'Handling feed #{index} {rules}')
                memory = await self.handle(rules)
                if memory:
                    feeds[index]['memory'] = memory
                    data.set('feeds', feeds)
        except asyncio.CancelledError:
            pass
        except Exception:
            await on_error(self.loop)

    @loop.before_loop
    async def loop_before(self):
        await self.bot.wait_until_ready()

    async def handle(self, rules):
        service_name = rules.get('service')
        proxy = services.get(Proxy, service_name, init=True)
        feed = services.get(Feed, service_name)

        if not proxy or not feed:
            log.warning(f'No matching service found for {service_name}')
            return

        channel = self.bot.get_channel(rules.get('channel'))
        webhooks = rules.get('webhooks', [])
        if not channel and not webhooks:
            log.warning(f'No matching destination')
            return

        api = proxy.login(user_id=rules.get('discord_user'))
        if not api:
            return

        if self.IGNORE_MEMORY:
            del rules['memory']
        result = feed.handle(api, rules)
        for result in result.get('result', [])[:self.RESULTS_LIMIT]:
            result['files'] = [
                {'file': self.download(x.get('url')), 'name': x.get('name')}
                for x in result.get('files', [])[:self.PICS_LIMIT]
            ]
            if channel:
                await self.post(result, channel)
            if webhooks:
                hook = DiscordWebhook(
                    webhooks,
                    content=result.get('content'),
                    **rules.get('webhook_options'),
                )
                for file in result.get('files', []):
                    hook.add_file(file=file.get('file'), filename=file.get('name'))
                hook.execute()
            time.sleep(self.WAIT_ITERATION_TIME)
        return result.get('memory')

    @staticmethod
    async def post(result, channel):
        result['files'] = [
            discord.File(x.get('file'), filename=x.get('name'))
            for x in result.get('files', [])
        ]
        await channel.send(**result)

    @staticmethod
    def download(url):
        log.debug(f'Downloading {url}')
        response = requests.get(url, headers={'referer': url})
        if response.status_code != 200:
            log.warning(response)
            return None
        return io.BytesIO(response.content)
