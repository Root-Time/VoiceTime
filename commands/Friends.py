import asyncio

import discord
from discord import Member, Guild
from discord.ext import commands
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle

from Module.get_database import fl
from Module.set_database import update_fl
from Utils.embed import embed, error, fs
from Utils.language import language
from classes.load_guild import LoadGuild


class Friends(commands.Cog):
    def __init__(self, client):
        self.client = client

    # ADD FRIEND
    @commands.command(aliases=['request', 'friend'])
    async def add(self, ctx, member: Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild
        if ctx.author.bot:
            return

        await ctx.message.delete()

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

        await ctx.send(embed=fs(l('{} und {} seit nun Freunde').format(author.mention, member.mention)),
                       delete_after=15)

    # REMOVE FRIEND
    @commands.command(aliases=['rem'])
    async def remove(self, ctx: Context, member: discord.Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild

        c: LoadGuild = LoadGuild(guild)

        if member is author:
            await ctx.channel.send(
                embed=embed('Error', 'Du kannst dich nicht selbst von deiner Freundesliste enfernen!', 10038562),
                delete_after=5)
            return

        if author not in fl.keys():
            await ctx.channel.send(embed=embed('Friend System', f'<@{author.id}> hat noch keine Freunde!', 10038562),
                                   delete_after=5)
            return

        if member not in fl[author]:
            await ctx.channel.send(
                embed=embed('Friend System', f'<@{author.id}> und <@{member.id}> wart nie Freunde!', 10038562),
                delete_after=5)
            return

        fl.get(author.id).remove(member.id)
        fl.get(member.id).remove(author.id)

        await ctx.channel.send(
            embed=embed('Friend System', f'<@{member.id}> und <@{author.id}> sind keine Freunde mehr!', 9936031),
            delete_after=5)

        # await c.logs.send(embed=embed('Friend System', f'<@{author.id}> hat <@{member.id}> von seiner Freundesliste
        # entfernt\n{datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}'))

    @commands.command()
    async def load(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        guild: Guild = ctx.guild

        author_fl = fl.get(member.id)
        if not author_fl:
            embed1 = embed('Friend List', f'<@{member.id}> hat noch keine Freunde!', 10038562)
            embed1.set_author(name=member.display_name, icon_url=member.avatar_url)
            await ctx.channel.send(embed=embed1, delete_after=10)
            return

        c = LoadGuild(guild)
        l = lambda _text: language(_text, c.lang)

        text = '\n'.join(f'<@{friend}>' for friend in author_fl)

        friends_list_embed = discord.Embed(title='Friend List', description=text, colour=15105570)
        friends_list_embed.set_author(name=member.display_name, icon_url=member.avatar_url)

        mess = await ctx.send(embed=friends_list_embed, components=[[
            Button(label='Schließen', style=ButtonStyle.red)
        ]])

        while True:
            try:
                event = await self.client.wait_for('button_click',
                                                   check=lambda _event: _event.message == mess,
                                                   timeout=30)
            except asyncio.TimeoutError:
                await mess.edit(components=[])
                return
            if event.author in [ctx.author, member]:
                await event.message.delete()
                return
            await event.respond(embed=error(l('Das kannst du nicht!')))


def setup(client):
    client.add_cog(Friends(client))
