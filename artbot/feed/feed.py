class Feed:
    FEEDS = {}

    @classmethod
    def handle(cls, api, watcher):
        type = watcher.get('type')
        if type not in cls.FEEDS:
            return
        return getattr(cls, cls.FEEDS[type])(api, watcher)
