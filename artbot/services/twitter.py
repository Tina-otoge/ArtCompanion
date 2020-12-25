import twitter

from .. import config
from .ReactionService import Service

class Twitter(Service):
    def __init__(self):
        super().__init__(
            extracters=[
                r'http(?:s)?:\/\/(?:www)?twitter\.com\/[a-zA-Z0-9_]+\/status\/(\d+)'
            ],
            triggers={
                '❤️': 'twitter_like',
                '🔁': 'twitter_retweet',
                # '👀': 'twitter_follow',
            },
            data_key='twitter_users',
            authenticator=self.twitter_login,
        )

    @staticmethod
    def twitter_login(credentials):
        key, secret = config.get('twitter_key'), config.get('twitter_secret')
        return twitter.Api(key, secret, credentials[0], credentials[1])

    @staticmethod
    def twitter_like(api: twitter.Api, status_id):
        api.CreateFavorite(status_id=status_id)

    @staticmethod
    def twitter_retweet(api: twitter.Api, status_id):
        api.PostRetweet(status_id)
