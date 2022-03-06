import json
import logging
import tweepy

from .feed import Feed
from ..proxy.twitter import TwitterAPIs

log = logging.getLogger(__name__)

class Twitter(Feed):
    FEEDS = {'list': 'twitter_list'}

    @staticmethod
    def dump_result(result, name='dump'):
        with open(f'twitter_{name}.json', 'w') as f:
            json.dump({"results": [x._json for x in result]}, f, indent=2)
            log.debug(f'Dumped Twitter response "{name}"')

    @staticmethod
    def filter_pics(x: tweepy.Tweet):
        return 'media' in x.entities and x.entities['media'][0]['type'] == 'photo'

    @classmethod
    def twitter_list(cls, api: TwitterAPIs, watcher):
        last_id = watcher.get('memory', {}).get('last_id', 0)
        posts = api.tweepy.list_timeline(
            slug=watcher.get('name'), owner_screen_name=watcher.get('owner'),
            include_rts=watcher.get('retweets', False),
            count=200,
        )
        cls.dump_result(posts)
        if posts:
            posts = filter(lambda x: x.id > last_id, posts)
            if watcher.get('pics_only', False):
                posts = filter(cls.filter_pics, posts)
            posts = sorted(posts, key=lambda x: x.id)
            last_id = posts[-1].id
        cls.dump_result(posts, 'filtered')
        return {
            'memory': {'last_id': last_id},
            'result': [cls.content_from_tweet(x) for x in posts]
        }

    @staticmethod
    def content_from_tweet(x: tweepy.Tweet):
        if not hasattr(x, 'retweeted_status'):
            content = f'https://twitter.com/{x.user.screen_name}/status/{x.id}'
        else:
            content = f'https://twitter.com/{x.retweeted_status.user.screen_name}/status/{x.retweeted_status.id}'
            content += f'\nRetweeted 🔁 by {x.user.name}'
            content += f'\n(<https://twitter.com/{x.user.screen_name}>)'
        if hasattr(x, 'extended_entities'):
            nb_pics = len(x.extended_entities['media'])
            if nb_pics > 1:
                content += f'\n{nb_pics} PICS'
        return {'content': content}
