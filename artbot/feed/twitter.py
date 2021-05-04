import json
import logging
import tweepy

from .feed import Feed
from ..proxy.twitter import TwitterAPIs

log = logging.getLogger(__name__)

class Twitter(Feed):
    FEEDS = {'list': 'twitter_list'}

    @classmethod
    def twitter_list(cls, api: TwitterAPIs, watcher):
        last_id = watcher.get('memory', {}).get('last_id', 0)
        posts = api.tweepy.list_timeline(
            slug=watcher.get('name'), owner_screen_name=watcher.get('owner'),
            include_rts=watcher.get('retweets', False),
            count=200,
        )
        with open('twitter_dump.json', 'w') as f:
            json.dump({"results": [x._json for x in posts]}, f, indent=2)
            log.debug('Dumped Twitter response')
        if posts:
            posts = filter(lambda x: x.id > last_id, posts)
            if watcher.get('pics_only', False):
                posts = filter(lambda x: 'media' in x.entities, posts)
            posts = sorted(posts, key=lambda x: x.id)
            last_id = posts[-1].id
        return {
            'memory': {'last_id': last_id},
            'result': [cls.content_from_tweet(x) for x in posts]
        }

    @staticmethod
    def content_from_tweet(x: tweepy.Status):
        content = f'https://twitter.com/user/status/{x.id}'
        if x.text.startswith('RT '):
            content += f'\nRetweeted 🔁 by {x.user.name}'
            content += f'\n(<https://twitter.com/{x.user.screen_name}>)'
        return {'content': content}

