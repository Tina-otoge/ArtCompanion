"""
Module to ease the manipulation of subclasses of a specific class, usually
representing the implementation for a service, for example Proxy->Twitter, or
Feed->Pixiv
"""


def all(class_, init=False):
    result = class_.__subclasses__()
    if init:
        result = [x() for x in result]
    return result


def get(class_, name, init=False):
    name = name.lower()
    for c in all(class_):
        if c.__name__.lower() == name:
            return c() if init else c
    return None
