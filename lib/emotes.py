import json
from . import config

def get_data():
    with open(config.get_emotes_path(), "rb") as file:
        data = json.load(file)
    return data


def get_emote(name: str):
    for emote in get_data():
        if name in str(emote['aliases']):
            return emote['emoji']
    return None

def __getattr__(name):
    return get_emote(name)

def __dir__():
    aliases = []
    for emote in get_data():
        aliases.extend(emote['aliases'])
    return aliases
