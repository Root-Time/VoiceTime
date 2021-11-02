import discord.errors

from Utils.embed import embed


def manage_channel(guild):
    return guild.me.guild_permissions.manage_channels


def send_message(guild):
    return guild.me.guild_permissions.send_messages


async def create_channel(c, name, type):
    guild = c.guild
    if not manage_channel(guild):
        return await no_permissions(c,
                             "Can't create Channels!!!\n Need Permissions to create Text Channels / Voice Channels!")
    if type == 'text':
        return await guild.create_text_channel(name)
    return await guild.create_voice_channel(name)


async def no_permissions(c, permissions):
    guild = c.guild
    if not c.config:
        if not manage_channel(guild):
            for channel in guild.text_channels:
                permissions = channel.permissions_for(guild.me)
                if permissions.send_messages:
                    await channel.send(guild.owner.mention)
                    await channel.send(embed=embed("Critical Error!!!", permissions, 'r'))
                    return

    if not send_message(guild):
        try:
            await guild.owner.send(
                embed=embed('Critical Error!!!', f'{guild}\n Can\'t send Messages\n!!!' + permissions, 'r'))
        except discord.errors.Forbidden:
            pass
        return

    await c.config.send(guild.owner.mention)
    await c.config.send(embed=embed('Critical Error!!!', permissions, 'r'))
