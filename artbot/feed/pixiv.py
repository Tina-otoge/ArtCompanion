import logging
import json

from .feed import Feed
from ..proxy.pixiv import PixivAPIs

log = logging.getLogger(__name__)

class Pixiv(Feed):
    FEEDS = {'following': 'pixiv_following'}

    TAGS_TR = {
        'オリジナル': 'original'
    }
    TAGS_STRONG = ['original']

    @classmethod
    def pixiv_following(cls, api: PixivAPIs, watcher):
        posts = api.papi.me_following_works(
            include_stats=False,
            include_sanity_level=False,
            image_sizes=['large', 'medium']
        ).get('response', [])
        posts = [
            api.papi.works(x.id).get('response', [x])[0] if x.is_manga else x
            for x in posts
        ]
        return cls.message_from_posts(posts, watcher)

    @classmethod
    def message_from_posts(cls, posts, watcher):
        with open('dump.json', 'w') as f:
            json.dump(posts, f, indent=2)
            log.debug('Dumped Pixiv response')
        memory = watcher.get('memory', {})
        last_id = memory.get('last_id', 0)
        posts = list(filter(lambda x: x.id > last_id, posts))
        posts.sort(key=lambda x: x.id)
        memory = {'last_id': posts[-1].id} if posts else None
        result = [
            cls.message_from_post(x) for x in posts
            if cls.verify_nsfw(x, watcher.get('safe'))
        ]
        return {
            'memory': memory,
            'result': result,
        }

    @staticmethod
    def get_files(post) -> list:
        urls = (
            [x.image_urls for x in post.metadata.pages]
            if post.is_manga
            else [post.image_urls]
        )
        png = urls[0].large.endswith('.png')
        size = 'medium' if (post.is_manga or (png and post.width > 2000)) else 'large'
        return [
            {
                'url': x[size],
                'name': f'pixiv_{post.id}_page{i}.{"png" if png else "jpg"}'
            } for i, x in enumerate(urls)
        ]


    @classmethod
    def message_from_post(cls, post) -> dict:
        link = f'<https://www.pixiv.net/artworks/{post.id}>'
        log.debug(f'Parsing pixiv post {link}')
        title = post.title
        artist = f'{post.user.name} ({post.user.account})'
        tags = [f'{x} (**{cls.TAGS_TR[x]}**)' if x in cls.TAGS_TR else x for x in post.tags]
        content = [
            link,
            f'{title} by {artist}',
            'Tags: ' + ', '.join(tags),
        ]
        if post.type == 'ugoira':
            content.append('This is an animation (うごイラ) 📹')
        return {
            'content': '\n'.join(content),
            'files': cls.get_files(post),
        }

    @staticmethod
    def verify_nsfw(post, safe=None):
        if safe is None:
            return True
        post_safe = post.age_limit == 'all-age'
        return post_safe == safe
