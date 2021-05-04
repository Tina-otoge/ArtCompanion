from artbot import config


class Feed:
    FEEDS = {}
    # Use author name and avatar as webhook
    RICH_WEBHOOK = config.get('rich_webhook', False)

    @classmethod
    def handle(cls, api, watcher):
        type = watcher.get('type')
        if type not in cls.FEEDS:
            return
        return getattr(cls, cls.FEEDS[type])(api, watcher)
