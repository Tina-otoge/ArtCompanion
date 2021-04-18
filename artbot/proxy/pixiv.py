import logging
from pixivpy3 import AppPixivAPI, PixivAPI

from .proxy import Proxy

log = logging.getLogger(__name__)

class PixivAPIs:
    def __init__(self, credentials):
        self.apapi = AppPixivAPI()
        self.papi = PixivAPI()
        self.apapi.auth(refresh_token=credentials[0])
        self.papi.auth(refresh_token=credentials[0])

class Pixiv(Proxy):
    def __init__(self):
        super().__init__(
            extracters=[
                r'https://(?:www\.)?pixiv\.net/(?:\w{2}/)?artworks/(\d+)',
                r'https://(?:www\.)?pixiv\.net/member_illust\.php\?(?:.*)?illust_id=(\d+)(?:.*)?',
            ],
            triggers={
                '❤️': 'pixiv_like',
                # '👀': 'pixiv_follow',
            },
            data_key='pixiv_users',
            authenticator=self.pixiv_login,
        )

    @staticmethod
    def pixiv_login(credentials):
        return PixivAPIs(credentials)

    @staticmethod
    def pixiv_like(api: PixivAPIs, work_id):
        result = api.apapi.illust_bookmark_add(work_id)
        log.debug(f'Pixiv liked {result}')
