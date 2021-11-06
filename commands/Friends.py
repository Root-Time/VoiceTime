import discord
from discord import Member, Guild, Interaction, ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button

from Module.get_database import fl
from Module.set_database import update_fl
from Utils.embed import embed, error, fs
from Utils.language import language
from classes.button import NewButton, view, clear_button
from classes.load_guild import LoadGuild


class Friends(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['request', 'friend'])
    async def add(self, ctx, member: Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild
        if ctx.author.bot:
            return

        if author == member:
            return await ctx.send(
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

        async def accept_friend_button(interaction: Interaction, button: Button):
            if interaction.user != member:
                await interaction.response.send_message(
                    embed=error(l('Du bist nicht dazu berechtigt!')), ephemeral=True
                )
                return

            await interaction.message.delete()

            if button.label == l('Nein'):
                mess_ping2 = await ctx.send(author.mention)
                await mess_ping2.delete()
                await ctx.send(embed=error(l('Deine Anfrage würde abgelehnt!')), delete_after=15)
                return

            fl.setdefault(author.id, []).append(member.id)
            fl.setdefault(member.id, []).append(author.id)
            update_fl()

            await ctx.send(embed=fs(l('{} und {} seit nun Freunde').format(author.mention, member.mention)),
                           delete_after=15)

        await ctx.channel.send(
            embed=embed(
                'Friend System',
                f'<@{member.id}>\n<@{ctx.author.id}> hat dir eine Freundschaftsanfrage geschickt!',
                'b'
            ), view=view(
                NewButton(l('Ja'), ButtonStyle.primary, accept_friend_button),
                NewButton(l('Nein'), ButtonStyle.danger, accept_friend_button),

            )
        )

    # REMOVE FRIEND
    @commands.command(aliases=['rem'])
    async def remove(self, ctx: Context, member: discord.Member):
        author: Member = ctx.author
        guild: Guild = ctx.guild

        c: LoadGuild = LoadGuild(guild)

        if member is author:
            await ctx.channel.send(
                embed=embed('Error', 'Du kannst dich nicht selbst von deiner Freundesliste entfernen!', 10038562),
                delete_after=5)
            return

        if author.id not in fl.keys():
            await ctx.channel.send(embed=embed('Friend System', f'<@{author.id}> hat noch keine Freunde!', 10038562),
                                   delete_after=5)
            return

        if member.id not in fl[author.id]:
            await ctx.channel.send(
                embed=embed('Friend System', f'<@{author.id}> und <@{member.id}> wart nie Freunde!', 10038562),
                delete_after=5)
            return

        fl.get(author.id).remove(member.id)
        fl.get(member.id).remove(author.id)
        update_fl()

        await ctx.channel.send(
            embed=embed('Friend System', f'<@{member.id}> und <@{author.id}> sind keine Freunde mehr!', 'o'),
            delete_after=5)

        """
        await c.logs.send(embed=embed('Friend System', f'<@{author.id}> hat <@{member.id}> von seiner Freundesliste
         entfernt\n{datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}'))
        """

    @commands.command()
    async def load(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        guild: Guild = ctx.guild

        author_fl = fl.get(member.id)
        if not author_fl:
            embed1 = embed('Friend List', f'<@{member.id}> hat noch keine Freunde!', 10038562)
            embed1.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            await ctx.channel.send(embed=embed1, delete_after=10)
            return

        c = LoadGuild(guild)
        l = lambda _text: language(_text, c.lang)

        text = '\n'.join(f'<@{friend}>' for friend in author_fl)

        friends_list_embed = discord.Embed(title='Friend List', description=text, colour=15105570)
        friends_list_embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)

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
    client.add_cog(Friends(client))
