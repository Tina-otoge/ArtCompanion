import re

PIXIV_ARTWORK_LINK_RE = re.compile(r'https://www\.pixiv\.net/(?:\w{2}/)?artworks/(\d+)')
PIXIV_ARTWORK_LINK_OLD_RE = re.compile(r'https://www\.pixiv\.net/member_illust\.php\?(?:.*)?illust_id=(\d+)(?:.*)?')

def extract_id(s: str):
    matches = (
        re.search(PIXIV_ARTWORK_LINK_RE, s) or
        re.search(PIXIV_ARTWORK_LINK_OLD_RE, s)
    )
    if matches is None:
        return None
    return matches.group(1)
