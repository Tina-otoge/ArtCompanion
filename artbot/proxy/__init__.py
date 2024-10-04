from .cog import ProxyCog


def init(bot):
    bot.add_cog(ProxyCog(bot))


from . import pixiv, twitter
