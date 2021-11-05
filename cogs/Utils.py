import discord, json, copy
from discord.ext import commands

from Module.get_database import voice
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def delete(self, ctx):
        for channel in ctx.guild.channels:
            try:
                if 'timeout' in channel.name.lower() or 'hiddenstorm' in channel.name.lower():
                    await channel.delete()
            except:
                continue

    @commands.command()
    async def voice_info(self, ctx):
        await ctx.send(voice)

    @commands.command()
    async def save(self, ctx):
        member = ctx.author
        guild = ctx.guild
        channel = member.voice.channel if member.voice else None

        try:
            c: LoadGuild = LoadGuild(guild)
        except:
            return

        vt: VoiceClass = c.get_channel(channel)

        print('Data', vt.save())


def setup(client):
    client.add_cog(Utils(client))
