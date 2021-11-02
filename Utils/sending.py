import asyncio

import discord




async def send(channel, *args, **kwargs):
    """
    channel -> Discord Channel,
    Button -> ButtonTyp
    Message -> str,
    embed (Title, Text, Color or (Format), (Format)) -> tuple,
    time (Delete After) -> Int, float,
    check(for wait) -> function,
    """
    embed = kwargs.get('embed')
    time = kwargs.get('time')
    check = kwargs.get('check')
    Message = kwargs.get('mess') or kwargs.get('Message')
    # load
    lang = 'de'

    if isinstance(embed, tuple):
        text = language(embed[1], lang)
        if len(embed) == 3:
            if isinstance(embed[2], tuple):
                _format = embed[2]
            else:
                colour = embed[2]
                _format = None
        elif len(embed) == 4:
            colour = embed[2]
            _format = embed[3]
        else:
            _format = None
            colour = None

        if _format:
            if isinstance(_format, str):
                text = text.format(_format)
            else:
                text = text.format(*_format)

        if colour in ['blue', 'b']:
            colour = 3447003  # blue
        elif colour in ['red', 'r']:
            colour = 15158332  # red
        elif colour in ['green', 'g']:
            colour = 3066993  # green
        elif colour in ['orange', 'o']:
            colour = 15105570  # orange
        else:
            colour = 0

        embed = discord.Embed(title=embed[0], description=text, colour=colour)

    mess = await channel.send(Message, embed=embed, delete_after=time, components=[[i for i in args]] if args else None)

    if not check:
        return mess

    while True:
        try:
            event = await client.wait_for('button_click', check=lambda event: event.message == mess, timeout=time)
        except asyncio.TimeoutError:
            event = None
        if await check(event): return event