import twitter
import tweepy

from artbot import config
from .proxy import Proxy

class TwitterAPIs:
    def __init__(self, credentials):
        key, secret = config.get('twitter_key'), config.get('twitter_secret')
        self.twitter = twitter.Api(key, secret, credentials[0], credentials[1])
        tweepy_auth = tweepy.OAuthHandler(key, secret)
        tweepy_auth.set_access_token(credentials[0], credentials[1])
        self.tweepy = tweepy.API(tweepy_auth)


class Twitter(Proxy):
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
        return TwitterAPIs(credentials)

    @staticmethod
    def twitter_like(api: TwitterAPIs, status_id):
        api.twitter.CreateFavorite(status_id=status_id)

    @staticmethod
    def twitter_retweet(api: TwitterAPIs, status_id):
        api.twitter.PostRetweet(status_id)
