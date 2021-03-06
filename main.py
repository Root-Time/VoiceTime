import asyncio
from datetime import datetime
import discord
import json

import yaml
from discord import ButtonStyle, Button, Interaction, Member, User
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MemberNotFound, MissingRequiredArgument, Context

from Module.get_database import get_client
from Utils.embed import embed, empty
from classes.button import view, NewButton

with open("Data/token.json", "r") as f:
    TokenList = json.load(f) or print("error")

with open("Data/config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader) or print("error")
    PREFIX = config.get('prefix')

Token = TokenList["VoiceTime"]
INTENTS = discord.Intents.all()

client: discord.client = commands.Bot(command_prefix=PREFIX, intents=INTENTS, description='Version 2.0.0a5-3rw8')
get_client(client)


@client.command()
async def test(ctx: Context):
    print(ctx)
    channel = ctx.author.voice.channel


# DiscordComponents(client)


# @client.slash_command(guild_ids=[410475041277345853])
# async def hello(ctx, name: str = None):
#     name = name or ctx.author.name
#     await ctx.respong(f"Hello {name}!")
#
#
# @client.user_command(name="Say Hello")
# async def hi(ctx, user):
#     await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")


@client.command()
async def lol(ctx):
    async def button1(interaction: Interaction):
        await interaction.user.send('HEY HOO')

    async def button2(interaction: Interaction):
        await interaction.channel.send('LELLELELLEL')

    await ctx.send('Hello', view=view(
        NewButton(label='Ja', style=ButtonStyle.primary, call=button1),
        NewButton(label='Nein', style=ButtonStyle.secondary, call=button2)
    ))

    test = view(
        NewButton(label='Ja', style=ButtonStyle.primary, call=button1),
        NewButton(label='Nein', style=ButtonStyle.secondary, call=button2)
    )
    print(test.children)


@client.command()
async def ola(ctx):
    id = 902650948617404456
    member: User = await client.fetch_user(505408682788388864)
    print(member)
    print(member.display_name)


@client.event
async def on_ready():
    print(f'>>>>  {client.user.name}  <<<<')
    print('>>>> ', datetime.now().strftime("%H:%M:%S"), ' <<<<')
    print('--------------------')

    async def status():
        while True:
            await client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="version 2.0.0.a5-3rw8"
            ))
            await asyncio.sleep(3)
            await client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Voice Temp Channel Bot"
            ))
            await asyncio.sleep(3)

    client.loop.create_task(status())


# # Voice
client.load_extension("events.VoiceCreate")
client.load_extension('events.VoiceLeave')
client.load_extension('events.VoiceJoin')
#

# # Commands
client.load_extension("commands.Friends")
# client.load_extension("commands.Friend_Slash")
client.load_extension("commands.Block")
# client.load_extension("commands.Block_Slash")
client.load_extension("commands.VoiceCommands")
# # TODO own cog for Friend & Block

# # Utils
client.load_extension("cogs.DevTools")
client.load_extension('cogs.Regain')


# # bot.load_extension("cogs.newServer")
# # bot.load_extension("cogs.Languages_Converter")#
# # bot.load_extension("cogs.setting")


# Error Handling
@client.event
async def on_command_error(ctx, error):
    if type(error) in [CommandNotFound]:
        return

    if isinstance(error, MissingRequiredArgument):
        if 'member is a required argument that is missing.' in str(error):
            await ctx.reply(embed=embed(None, 'Du musst noch einen Member eintragen!', 'r'), delete_after=15)
            return
        await ctx.reply(embed=embed(None, 'Du hast einen Parameter vergessen!', 'r'), delete_after=15)
        return

    if isinstance(error, MemberNotFound):
        return await ctx.channel.reply(embed=embed(None, 'Du hast keinen g??ltigen Namen eingegeben', 10038562),
                                       delete_after=5)
    raise error


client.run(Token)
