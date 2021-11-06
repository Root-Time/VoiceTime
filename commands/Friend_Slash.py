import asyncio

import discord
from discord import Member, Guild, ApplicationContext, Interaction
from discord.ext import commands
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle

from Module.get_database import fl
from Module.set_database import update_fl
from Utils.embed import embed, error, fs, empty
from Utils.language import language
from classes.load_guild import LoadGuild


class FriendSlash(commands.Cog):
    def __init__(self, client):
        self.client = client

    # ADD FRIEND
    @commands.slash_command(name='add',  description='Add a new voice friend!', guild_ids=[410475041277345853])
    async def add(self, ctx: ApplicationContext, member: discord.Member):
        author: Member = ctx.user
        guild: Guild = ctx.guild
        if author.bot:
            return

        if author == member:
            return await ctx.respond(
                embed=empty('Du kannst dir selber keine Freundschaftsanfrage schicken!', 10038562),
                delete_after=5)

        c: LoadGuild = LoadGuild(guild)
        l = lambda text: language(text, c.lang)

        if member.id in fl.get(author.id, []):
            await ctx.respond(
                embed=embed('Friend System', f'<@{author.id}> und <@{member.id}> sind schon befreundet!', 10038562),
                delete_after=5)
            return

        mess: Interaction = await ctx.respond(member.mention)

        mess = await ctx.channel.send(
            embed=embed(
                'Friend System',
                f'<@{member.id}>\n<@{author.id}> hat dir eine Freundschaftsanfrage geschickt!',
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
    @commands.slash_command(name='remove', description='Remove a Friend!')
    async def remove(self, ctx: ApplicationContext, member: discord.Member):
        author: Member = ctx.user
        guild: Guild = ctx.guild

        c: LoadGuild = LoadGuild(guild)

        if member is author:
            await ctx.respond(
                embed=embed(None, 'Du kannst dich nicht selbst von deiner Freundesliste enfernen!', 10038562),
                delete_after=5)
            return

        if author.id not in fl.keys():
            await ctx.respond(embed=embed('Friend System', f'<@{author.id}> hat noch keine Freunde!', 10038562),
                              delete_after=5)
            return

        if member.id not in fl[author.id]:
            await ctx.respond(
                embed=embed('Friend System', f'<@{author.id}> und <@{member.id}> wart nie Freunde!', 10038562),
                delete_after=5)
            return

        fl.get(author.id).remove(member.id)
        fl.get(member.id).remove(author.id)
        update_fl()

        await ctx.respond(
            embed=embed('Friend System', f'<@{member.id}> und <@{author.id}> sind keine Freunde mehr!', 'o'),
            delete_after=5)

        # await c.logs.send(embed=embed('Friend System', f'<@{author.id}> hat <@{member.id}> von seiner Freundesliste
        # entfernt\n{datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}'))

    @commands.slash_command(name='load', description='Load a friend list')
    async def load(self, ctx: ApplicationContext, member: discord.Member = None):
        if not member:
            member = ctx.user

        guild: Guild = ctx.guild

        author_fl = fl.get(member.id)
        if not author_fl:
            embed1 = embed('Friend List', f'<@{member.id}> hat noch keine Freunde!', 10038562)
            embed1.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            await ctx.respond(embed=embed1, delete_after=10)
            return

        c = LoadGuild(guild)
        l = lambda _text: language(_text, c.lang)

        text = '\n'.join(f'<@{friend}>' for friend in author_fl)

        friends_list_embed = discord.Embed(title='Friend List', description=text, colour=15105570)
        friends_list_embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)

        mess = await ctx.respond(embed=friends_list_embed, components=[[
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
    client.add_cog(FriendSlash(client))
