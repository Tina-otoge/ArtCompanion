import json
import logging

from artbot import config
from artbot.storage import Storage

from ..proxy.pixiv import PixivAPIs
from .feed import Feed

log = logging.getLogger(__name__)


class Pixiv(Feed):
    FEEDS = {"following": "pixiv_following"}
    TRANSLATIONS = Storage("translations.json")

    @classmethod
    def pixiv_following(cls, api: PixivAPIs, watcher):
        posts = api.apapi.illust_follow()
        with open("pixiv_dump.json", "w") as f:
            json.dump(posts, f, indent=2)
            log.debug("Dumped Pixiv response")
        posts = posts.get("illusts", [])
        return cls.message_from_posts(posts, watcher)

    @classmethod
    def message_from_posts(cls, posts, watcher):
        memory = watcher.get("memory", {})
        last_id = memory.get("last_id", 0)
        posts = list(filter(lambda x: x.id > last_id, posts))
        posts.sort(key=lambda x: x.id)
        memory = {"last_id": posts[-1].id} if posts else None
        result = [
            cls.message_from_post(x)
            for x in posts
            if all(
                [
                    cls.verify_nsfw(x, watcher.get("safe")),
                    cls.verify_tags_whitelist(x, watcher.get("whitelist")),
                    cls.verify_tags_blacklist(x, watcher.get("blacklist")),
                ]
            )
        ]
        log.debug(f"Got {len(result)} posts")
        return {
            "memory": memory,
            "result": result,
        }

    @staticmethod
    def get_files(post) -> list:
        urls = (
            [x.image_urls for x in post.meta_pages]
            if post.page_count > 1
            else [post.image_urls]
        )
        png = urls[0].large.endswith(".png")
        # size = 'medium' if (post.is_manga or (png and post.width > 2000)) else 'large'
        size = "large"
        proxy = config.get("pixiv_proxy")
        if proxy:
            for x in urls:
                x[size] = x[size].replace("//i.pximg.net/", f"//{proxy}/")
        return [
            {
                "url": x[size],
                "name": f'pixiv_{post.id}_page{i}.{"png" if png else "jpg"}',
            }
            for i, x in enumerate(urls)
        ]

    @classmethod
    def message_from_post(cls, post) -> dict:
        link = f"<https://www.pixiv.net/artworks/{post.id}>"
        log.debug(f"Parsing pixiv post {link}")
        title = post.title
        artist = f"{post.user.name} ({post.user.account})"
        tags = [
            f"{x.name} ({x.translated_name})" if x.translated_name else x.name
            for x in post.tags
        ]
        content = [
            link,
            f"{title} by {artist}",
            "Tags: " + ", ".join(tags),
        ]
        if post.type == "ugoira":
            content.append("This is an animation (うごイラ) 📹")
        options = {}
        if cls.RICH_WEBHOOK:
            # options['avatar_url'] = list(post.user.profile_image_urls.values())[0]
            options["username"] = f"{artist} on Pixiv"
        return {
            "content": "\n".join(content),
            "files": cls.get_files(post),
            **options,
        }

    @staticmethod
    def verify_nsfw(post, safe=None):
        if safe is None:
            return True
        post_safe = post.x_restrict == 0
        return post_safe == safe

    @staticmethod
    def verify_tags_blacklist(post, blacklist=None):
        """Returns false if any tag from the post is found in blacklist"""
        if not blacklist:
            return True
        for tag in post.tags:
            if tag.name in blacklist:
                log.info(f"Found blacklisted tag {tag}")
                return False
        return True

    @staticmethod
    def verify_tags_whitelist(post, whitelist=None):
        """Returns true if any tag in the whitelist is found in post"""
        if not whitelist:
            return True
        for tag in whitelist:
            if tag.name in post.tags:
                return True
        return False
