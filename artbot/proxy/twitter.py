import logging
import functools
import twitter
import tweepy

from artbot import config
from .proxy import Proxy

log = logging.getLogger(__name__)

TWITTER_API_ALREADY_FAVORITED_CODE = 139
TWITTER_API_ALREADY_RETWEETED_CODE = 327

def ignore_error(codes=None):
    if not codes:
        codes = []
    elif not isinstance(codes, list):
            codes = [codes]
    def inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except twitter.TwitterError as e:
                error = e.message[0]
                if error['code'] in codes:
                    log.debug(f'Ignoring error {error}')
        return wrapper
    return inner


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
    @ignore_error(TWITTER_API_ALREADY_FAVORITED_CODE)
    def twitter_like(api: TwitterAPIs, status_id):
        api.twitter.CreateFavorite(status_id=status_id)

    @staticmethod
    @ignore_error(TWITTER_API_ALREADY_RETWEETED_CODE)
    def twitter_retweet(api: TwitterAPIs, status_id):
        api.twitter.PostRetweet(status_id)
