import logging
import sys

import requests

from artbot import config


class WebhookHandler(logging.Handler):
    def emit(self, record):
        emit(self.format(record))


def emit(msg):
    webhook = config.get("error_webhook")
    if not webhook:
        return
    requests.post(
        webhook, json={"username": "Artbot reporting", "content": msg}
    )


def log(*msgs, sep="\n"):
    msg = sep.join(map(str, msgs))
    print(msg, file=sys.stderr)
    emit(msg)
