import discord, json, copy
from discord.ext import commands

from Module.get_database import voice


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def delete(self, ctx):
        for channel in ctx.guild.channels:
            if 'timeout' in channel.name.lower():
                await channel.delete()

    @commands.command()
    async def voice_info(self, ctx):
        await ctx.send(voice)


def setup(client):
    client.add_cog(Utils(client))
