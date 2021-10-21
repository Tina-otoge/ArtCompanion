import asyncio
from datetime import datetime
import io
import logging
import requests
import time
from arrow import Arrow
import discord
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook

from artbot import config, data, services, on_error
from .feed import Feed
from ..proxy.proxy import Proxy

log = logging.getLogger(__name__)

class FeedCog(commands.Cog):
    # Time between each post, avoid API limit
    WAIT_ITERATION_TIME = config.get('feed_post_wait', 2)
    # Limit the amount of posts to post. WARNING: will update memory like if all posts were posted
    # Change this to 0 for "dry" mode
    RESULTS_LIMIT = config.get('feed_posts_limit', None)
    # Limit of pics to post per post
    PICS_LIMIT = config.get('feed_pics_limit', 5)
    # Should the memory be ignored
    IGNORE_MEMORY = config.get('feed_ignore_memory', False)
    # Time before each iteration
    LOOP_TIME = config.get('feed_loop_time', {'hours': 1})

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.loop.start()
        self.update_status.start()

    @commands.command()
    async def watch(self, context: commands.Context, service, *args):
        """
        Bridges a feed to a Discord channel
        """
        raise NotImplementedError

    @tasks.loop(seconds=30)
    async def update_status(self):
        dt = self.loop.next_iteration
        if not dt:
            return
        time = Arrow.fromdatetime(self.loop.next_iteration)
        await self.bot.change_presence(activity=discord.Game(
            f'next feed {time.humanize()}'
        ))

    @tasks.loop(**LOOP_TIME)
    async def loop(self):
        try:
            feeds = data.get('feeds', [])
            for index, rules in enumerate(feeds):
                log.debug(f'Handling feed #{index} {rules}')
                await self.bot.change_presence(activity=discord.Game(
                    f'feed {index}'
                ))
                memory = await self.handle(rules)
                if memory:
                    log.debug(f'Updating memory to {memory}')
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
            log.warning('Could not login')
            return

        if self.IGNORE_MEMORY and 'memory' in rules:
            del rules['memory']
        result = feed.handle(api, rules)
        memory = result.get('memory')
        for result in result.get('result', [])[:self.RESULTS_LIMIT]:
            if len(result.get('files', [])) > self.PICS_LIMIT:
                result['content'] = (
                    result.get('content', '')
                    + f'\n({len(result["files"]) - self.PICS_LIMIT} more pictures not shown)'
                )
                result['files'] = result['files'][:self.PICS_LIMIT]
            try:
                result['files'] = [
                    {'file': self.download(x.get('url')), 'name': x.get('name')}
                    for x in result.get('files', [])
                ]
                if channel:
                    await self.post_channel(result, channel)
                if webhooks:
                    self.post_webhooks(result, webhooks, rules.get('webhook_options', {}))
            except Exception:
                log.error(f'Failed to post {result}')
                await on_error(self.handle)
            time.sleep(self.WAIT_ITERATION_TIME)
        return memory


    @staticmethod
    async def post_channel(result, channel):
        result['files'] = [
            discord.File(x.get('file'), filename=x.get('name'))
            for x in result.get('files', [])
        ]
        await channel.send(**result)

    @staticmethod
    def post_webhooks(result: dict, webhooks: str, options: dict):
        files = result.pop('files', [])
        options.update(result)
        hook = DiscordWebhook(
            webhooks,
            **options,
        )
        for file in files:
            hook.add_file(file=file.get('file'), filename=file.get('name'))
        hook.execute()

    @staticmethod
    def download(url):
        log.debug(f'Downloading {url}')
        response = requests.get(url, headers={'referer': url})
        if response.status_code != 200:
            log.warning(response)
            return None
        return io.BytesIO(response.content)
