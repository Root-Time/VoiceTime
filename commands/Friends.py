import discord, json, copy
from discord import Member, Guild
from discord.ext import commands
from discord_components import Button, ButtonStyle

from Module.get_database import voice, fl
from Module.set_database import update_fl
from Utils.embed import embed, error, fs
from Utils.language import language
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


class Friends(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def add(self, ctx, member: Member):
        if ctx.author.bot:
            return
        await ctx.message.delete()
        author: Member = ctx.author
        guild: Guild = ctx.guild

        if author == member:
            return await ctx.channel.send(
                embed=embed('Error', 'Du kannst dir selber keine Freundschaftsanfrage schicken!', 10038562),
                delete_after=5)

        c: LoadGuild = LoadGuild(guild)
        l = lambda text: language(text, c.lang)

        if member.id in fl.get(author.id, []):
            await ctx.channel.send(
                embed=embed('Friend System', f'<@{author.id}> und <@{member.id}> sind schon befreundet!', 10038562),
                delete_after=5)
            return

        mess_ping = await ctx.send(f'{member.mention}')
        await mess_ping.delete()

        mess = await ctx.channel.send(
            embed=embed(
                'Friend System',
                f'<@{member.id}>\n<@{ctx.author.id}> hat dir eine Freundschaftsanfrage geschickt!',
                'b'
            ),
            components=[
                [Button(label=l('ja'), style=ButtonStyle.blue, id='ja'),
                 Button(label=l('Nein'), style=ButtonStyle.red, id='nein')]
            ]
        )

        while True:
            event = await self.client.wait_for('button_click', check=lambda _event: _event.message == mess)
            if event.author != member:
                await event.respond(embed=error(l('Du bist nicht dazu berechtigt!')))
                continue
            break

        await event.respond(type=6)
        await mess.delete()

        if event.component.id == 'nein':
            mess_ping = await ctx.send(author.mention)
            await mess_ping.delete()
            await ctx.send(embed=error(l('Deine Anfrage würde abgelehnt!')), delete_after=15)
            return

        fl.setdefault(author.id, []).append(member.id)
        fl.setdefault(member.id, []).append(author.id)
        update_fl()

        await ctx.send(embed=fs(l('{} und {} seit nun Freunde').format(author.mention, member.mention)), delete_after=15)


def setup(client):
    client.add_cog(Friends(client))
