from discord.ext import commands

from Utils.embed import error
from classes.load_guild import LoadGuild


class VoiceCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def claim(self, ctx):
        guild = ctx.guild
        author = ctx.author
        try:
            c: LoadGuild = LoadGuild(guild)
            l = c.l
        except:
            return

        if not author.voice:
            await ctx.reply(embed=error(l('Du kannst nur einen Voice Channel claimen wenn du auch in dem drin bist!')))
            return

        vt = c.get_channel(author.voice.channel)

        if not vt:
            await ctx.reply(embed=error(l('Du musst in einem Voice Channel gehen wo man claimen kann!')))
            return


def setup(client):
    client.add_cog(VoiceCommands(client))
