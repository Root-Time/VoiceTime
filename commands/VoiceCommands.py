import asyncio
import time
from datetime import datetime

from discord.ext import commands
from discord.ext.commands import Context

from Utils.embed import error, vc_embed, embed, voice
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


class VoiceCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def claim(self, ctx: Context):
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

        vt: VoiceClass = c.get_channel(author.voice.channel)

        if not vt:
            await ctx.reply(embed=error(l('Du musst in einem Voice Channel gehen wo man claimen kann!')))
            return

        if not vt.claim_cooldown:
            await ctx.reply(embed=error(l('Der Owner {} ist immer noch im Channel drin!').format(vt.owner.mention)))
            return

        if vt.claim_cooldown > datetime.now():
            await ctx.reply(
                embed=error(l(
                    'Du kannst den Channel in <t:{}:R> ({} Sekunden) claimen'
                ).format(
                    int(time.time() + (vt.claim_cooldown - datetime.now()).total_seconds()),
                    int(
                        (vt.claim_cooldown - datetime.now()).total_seconds()
                    )
                ))
            )

            return
        vt.owner = ctx.author

        await c.setting.send(
            embed=vc_embed(
                l('{}\nDu bist nun der neue Owner vom Channel {}').format(ctx.author.mention, vt().mention)
            ), view=None
        )

        # TODO add more feature

    @commands.command()
    async def limit(self, ctx: Context, limit=None):
        guild = ctx.guild
        author = ctx.author

        c: LoadGuild = LoadGuild(guild)

        vt: VoiceClass = c.get_channel(author)

        if not vt:
            await ctx.message.reply(embed=error(c.l('Du brauchst einen Channel um den Channel zu limitieren!')))
            return

        await vt().edit(user_limit=limit)
        await ctx.reply(
            embed=voice(c.l('Erfolgreich!\nDer Channel ist nun {} limitiert').format(limit or 'nicht mehr'))
        )

    @commands.command()
    async def owner(self, ctx, member):
        guild = ctx.guild
        author = ctx.guild

        c = LoadGuild(guild)
        vt: VoiceClass = c.get_channel(author)

        if not vt:
            return await ctx.message.reply(
                embed=error(c.l('Du brauchst einen Channel um jemanden Owner zu transferieren')))

        vt.owner = member

        await ctx.channel.send(embed=voice(c.l('{} ist der neue Besitzer von {}').format(member.mention, vt().mention)))

        if member.voice:
            if member.voice.channel != vt():
                await ctx.send(embed=error(c.l('{} hat 3 Minuten um in den Channel zugehen').format(member.mention)))
                await vt.owner_disconnect()

        

def setup(client):
    client.add_cog(VoiceCommands(client))
