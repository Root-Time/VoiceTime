# Embed
import discord


def embed(title, description, c=0) -> discord.Embed:
    if c in ['blue', 'b']:
        c = 3447003  # blue
    elif c in ['red', 'r']:
        c = 15158332  # red
    elif c in ['green', 'g']:
        c = 3066993  # green
    elif c in ['orange', 'o']:
        c = 15105570  # orange
    if title:
        return discord.Embed(title=False, description=description, colour=c)
    return discord.Embed(description=description, colour=c)


def error(text):
    return embed(None, text, 'r')


def empty(text, c='b'):
    return embed(None, text, c)


def voice(text, color="blue"):
    return embed('VoiceTime', text, color)


def info(text):
    return embed('Info', text, 'o')


def e(text):
    return 'Error', text, 'r'


def v(text, color="blue"):
    return 'VoiceTime', text, color


def i(text):
    return 'Info', text, 'o'


def fs(text):
    return embed('Friend System', text, 'g')
