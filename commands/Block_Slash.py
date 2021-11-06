import discord
from discord import Member, Guild, ApplicationContext, Interaction, ButtonStyle
from discord.ext import commands

from Module.get_database import bl, owner_vc_list
from Module.set_database import update_bl
from Utils.embed import embed, error
from Utils.language import language
from classes.button import view, NewButton, clear_button
from classes.load_guild import LoadGuild


class BlockSlash(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Block
    @commands.slash_command(name='block', description='Block a user')
    async def block(self, ctx, member: discord.Member):
        author: Member = ctx.user
        guild: Guild = ctx.guild

        if member.bot:
            return

        if author == member:
            await ctx.respond(embed=error('Du kannst dich nicht selber blockieren!'),
                              delete_after=5)
            return

        if member.id in bl.get(author.id, []):
            await ctx.respond(embed=embed('Block List', f'<@{member.id}> ist schon blockiert!', 10038562),
                              delete_after=5)
            return

        bl.setdefault(author.id, []).append(member.id)
        update_bl()

        await ctx.respond(
            embed=embed('Block List', f'{member.mention} würde erfolgreich blockiert!', 9936031), delete_after=5)

        # Remove Member from VC System
        if author.id in owner_vc_list.keys():
            for _voice in owner_vc_list.get(author.id, []):
                if member in _voice.members:
                    await _voice().set_permissions(member, connect=False)
                    _voice.rem(member)
                    if member in _voice().members:
                        await member.move(None)

    @commands.slash_command(name='unblock', description='unblock a User')
    async def unblock(self, ctx: ApplicationContext, member: Member):
        author: Member = ctx.user
        guild: Guild = ctx.guild

        if member.bot:
            return

        c = LoadGuild(guild)
        l = lambda text: language(text, c.lang)

        if member == author:
            await ctx.respond(embed=error('Du kannst dich nicht selber entblocken?!'),
                              delete_after=5)
            return

        if member.id not in bl.get(author.id, []):
            await ctx.respond(embed=error(l('{}. Du hast {} nicht geblockt.').format(author.mention, member.mention)),
                              delete_after=15)
            return

        bl[author.id].remove(member.id)
        update_bl()

        await ctx.respond(
            embed=embed('Block List', l('{} wurde aus {} Block Liste entfernt').format(member.mention, author.mention),
                        9936031),
            delete_after=7
        )

    @commands.slash_command(name='blocklist', description='Show a Block List')
    async def bl(self, ctx: ApplicationContext, member: discord.Member = None):
        if not member:
            member = ctx.user

        guild: Guild = ctx.guild

        author_bl = bl.get(member.id)
        if not author_bl:
            embed1 = embed('Blocklist', f'<@{member.id}> hat noch niemand blockiert!', 10038562)
            embed1.set_author(name=member.display_name, icon_url=member.avatar_url)
            await ctx.respond(embed=embed1, delete_after=10)
            return

        c = LoadGuild(guild)
        l = lambda _text: language(_text, c.lang)

        text = '\n'.join(f'<@{friend}>' for friend in author_bl)

        friends_list_embed = discord.Embed(title='Block List', description=text, colour=15105570)
        friends_list_embed.set_author(name=member.display_name, icon_url=member.avatar_url)

        async def close_button(interaction: Interaction, _):
            if interaction.user in [ctx.author, member]:
                await interaction.message.delete()
                return
            await interaction.response.send_message(embed=error(l('Das kannst du nicht!')), ephemeral=True)

        mess = await ctx.send(
            embed=friends_list_embed,
            view=view(
                NewButton(l('Schließen'), ButtonStyle.danger, close_button)
            )
        )

        clear_button(mess, 15)


def setup(client):
    client.add_cog(BlockSlash(client))
