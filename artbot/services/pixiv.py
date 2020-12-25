from pixivpy3 import AppPixivAPI

from .ReactionService import Service

class Pixiv(Service):
    def __init__(self):
        super().__init__(
            extracters=[
                r'https://www\.pixiv\.net/(?:\w{2}/)?artworks/(\d+)',
                r'https://www\.pixiv\.net/member_illust\.php\?(?:.*)?illust_id=(\d+)(?:.*)?',
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
        result = AppPixivAPI()
        result.login(credentials[0], credentials[1])
        return result

    @staticmethod
    def pixiv_like(api, work_id):
        api.illust_bookmark_add(work_id)
