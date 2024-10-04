from .cog import FeedCog


def init(bot):
    bot.add_cog(FeedCog(bot))


from . import pixiv, twitter
