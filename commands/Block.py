import asyncio

import discord, json, copy
from discord import Member, Guild
from discord.ext import commands
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle

from Module.get_database import voice, fl, bl, owner_vc_list
from Module.set_database import update_fl, update_bl
from Utils.embed import embed, error, fs
from Utils.language import language
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


class Block(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Block
    @commands.command()
    async def block(self, ctx, member: discord.Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild

        if member.bot:
            return

        if author == member:
            await ctx.channel.send(embed=error('Du kannst dich nicht selber blockieren!'),
                                   delete_after=5)
            return

        if member.id in bl.get(author.id, []):
            await ctx.channel.send(embed=embed('Block List', f'<@{member.id}> ist schon blockiert!', 10038562),
                                   delete_after=5)
            return

        bl.setdefault(author.id, []).append(member.id)
        update_bl()

        await ctx.channel.send(
            embed=embed('Block List', f'{member.mention} würde erfolgreich blockiert!', 9936031), delete_after=5)

        # Remove Member from VC System
        if author.id in owner_vc_list.keys():
            for _voice in owner_vc_list.get(author.id, []):
                if member in _voice.members:
                    await _voice().set_permissions(member, connect=False)
                    _voice.rem(member)
                    if member in _voice().members:
                        await member.move(None)

    @commands.command()
    async def unblock(self, ctx: Context, member: Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild

        if member.bot:
            return

        c = LoadGuild(guild)
        l = lambda text: language(text, c.lang)

        if member == author:
            await ctx.channel.send(embed=error('Du kannst dich nicht selber entblocken?!'),
                                   delete_after=5)
            return

        if member.id not in bl.get(author.id, []):
            await ctx.send(embed=error(l('{}. Du hast {} nicht geblockt.').format(author.mention, member.mention)),
                           delete_after=15)
            return

        bl[author.id].remove(member.id)
        update_bl()

        await ctx.send(
            embed=embed('Block List', l('{} wurde aus {} Block Liste entfernt').format(member.mention, author.mention),
                        9936031),
            delete_after=7
        )

    @commands.command()
    async def bl(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        guild: Guild = ctx.guild

        author_bl = bl.get(member.id)
        if not author_bl:
            embed1 = embed('Block List', f'<@{member.id}> hat noch niemand blockiert!', 10038562)
            embed1.set_author(name=member.display_name, icon_url=member.avatar_url)
            await ctx.channel.send(embed=embed1, delete_after=10)
            return

        c = LoadGuild(guild)
        l = lambda _text: language(_text, c.lang)

        text = '\n'.join(f'<@{friend}>' for friend in author_bl)

        friends_list_embed = discord.Embed(title='Block List', description=text, colour=15105570)
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
    client.add_cog(Block(client))
