import logging
import re

import discord

from artbot import data

log = logging.getLogger(__name__)


class Proxy:
    def __init__(
        self,
        extracters=[],
        triggers={},
        data_key=None,
        authenticator=None,
        watchers={},
    ):
        self.extracters = [
            re.compile(x) if isinstance(x, str) else x for x in extracters
        ]
        self.triggers = triggers
        self.data_key = data_key
        self.authenticator = authenticator
        self.watchers = watchers

    def extract(self, s: str):
        for regex in self.extracters:
            matches = re.search(regex, s)
            if matches:
                return matches.group(1)

    def login(self, user: discord.User = None, user_id=None):
        user_id = user_id or str(user.id)
        credentials = self.get_users().get(user_id)
        if not credentials or not self.authenticator:
            return credentials
        log.debug(f"Logging in using {self.authenticator}")
        return self.authenticator(credentials)

    def get_users(self):
        return data.get(self.data_key, {})

    def save_users(self, users):
        data.set(self.data_key, users)
