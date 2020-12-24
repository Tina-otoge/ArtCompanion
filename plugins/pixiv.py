import json
import re
from disco.bot import Plugin
from pixivpy3 import AppPixivAPI, PixivError

from .utils import is_pm

PIXIV_ARTWORK_LINK_RE = re.compile(r'https://www\.pixiv\.net/(?:\w{2}/)?artworks/(\d+)')
PIXIV_ARTWORK_LINK_OLD_RE = re.compile(r'https://www\.pixiv\.net/member_illust\.php\?(?:.*)?illust_id=(\d+)(?:.*)?')
STORAGE_FILE = 'pixiv_users.json'

class PixivUser(dict):
    def __init__(self, username, password):
        dict.__init__(self, username=username, password=password)
        self.username = username
        self.password = password

class PixivPlugin(Plugin):
    TRIGGERS = {
        '❤️': None,
        # '👀': None,
    }

    def load(self, context):
        super(PixivPlugin, self).load(context)
        try:
            with open(STORAGE_FILE) as f:
                self.users = json.load(f)
        except (FileNotFoundError, TypeError):
            print('Could not load storage file')
            self.users = {}

    def save(self):
        with open(STORAGE_FILE, 'w') as f:
            json.dump(self.users, f)

    def login(self, user):
        self.api = AppPixivAPI()
        self.api.login(user.username, user.password)

    def logoff(self):
        self.api = None

    def bookmark_as(self, work_id, user):
        self.login(user)
        self.api.illust_bookmark_add(work_id)
        self.logoff()

    def get_user(self, id):
        user = self.users.get(str(id))
        if not user:
            return None
        return PixivUser(**user)

    @Plugin.command('register', '<username:str> <password:str>', group='pixiv')
    def register(self, event, username, password):
        user = PixivUser(username, password)
        try:
            self.api.login(user.username, user.password)
            self.users[event.msg.author.id] = user
            self.save()
            print('Pixiv registered {} as {}'.format(event.msg.author, user.username))
        except PixivError:
            event.msg.reply('Could not login, either the credentials are incorrect or Pixiv is currently unreachable')
        if not is_pm(event.msg):
            event.msg.delete()
            event.msg.reply('Deleted your message to hide your credentials')

    @Plugin.listen('MessageReactionAdd')
    def on_reaction_add(self, event):
        if self.client.state.me.id == event.user_id:
            return
        user = self.get_user(event.user_id)
        if not user or event.emoji.name not in self.TRIGGERS:
            return
        content = event.client.api.channels_messages_get(event.channel_id, event.message_id).content
        matches = re.search(PIXIV_ARTWORK_LINK_RE, content) or re.search(PIXIV_ARTWORK_LINK_OLD_RE, content)
        if matches is None:
            return
        print('Attempting to bookmark Pixiv picture...')
        work_id = int(matches.group(1))
        self.bookmark_as(work_id, user)
        print('Bookmarked {} on behalf of user {} as {}'.format(
            work_id, event.user_id, user.username
        ))

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        content = event.client.api.channels_messages_get(event.channel_id, event.id).content
        matches = re.search(PIXIV_ARTWORK_LINK_RE, content) or re.search(PIXIV_ARTWORK_LINK_OLD_RE, content)
        if matches is None:
            return
        print('Pixiv link detected, adding triggers...')
        for emoji in self.TRIGGERS:
            event.client.api.channels_messages_reactions_create(
                event.channel_id,
                event.id,
                emoji,
            )
