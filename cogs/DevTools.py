from discord.ext import commands
from discord.ext.commands import Context

from Module.get_database import voice, admins
from Utils.embed import error, embed
from classes.load_guild import LoadGuild


class DevTools(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> DevTools')

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
        pass  # Method not actual
        """
        member = ctx.author
        guild = ctx.guild
        channel = member.voice.channel if member.voice else None

        try:
            c: LoadGuild = LoadGuild(guild)
        except:
            return

        vt: VoiceClass = c.get_channel(channel)

        print('Data', vt.save())
        """

    @commands.command()
    async def vc_stats(self, ctx: Context):
        if ctx.author.id not in admins:
            await ctx.send(embed=error('Sry only for Bot Administrator'))
            return

        if ctx.author.voice:
            c = LoadGuild(ctx.guild)
            vt = c.get_channel(ctx.author.voice.channel)
            await ctx.send(embed=embed(
                vt().name,
                f"""
                Owner = {vt.owner};
                Member = {vt.members}
                """))


def setup(client):
    client.add_cog(DevTools(client))
