import asyncio
from datetime import datetime
import discord
import json

import yaml
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MemberNotFound
from discord_components import DiscordComponents

from Utils.embed import embed

with open("Data/token.json", "r") as f:
    TokenList = json.load(f) or print("error")

with open("Data/config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader) or print("error")
    PREFIX = config.get('prefix')

Token = TokenList["VoiceTime"]
INTENTS = discord.Intents.all()

client: discord.client = commands.Bot(command_prefix=PREFIX, intents=INTENTS, description='Version 2.0.0a5-3rw8')


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
    DiscordComponents(client)


# Voice
client.load_extension("events.VoiceCreate")
client.load_extension('events.VoiceLeave')
client.load_extension('events.VoiceJoin')

# Commands
# client.load_extension("cogs.Friends")
# TODO own cog for Friend & Block

# Utils
client.load_extension("cogs.Utils")


# bot.load_extension("cogs.newServer")
# bot.load_extension("cogs.Languages_Converter")#
# bot.load_extension("cogs.setting")


@client.command()
async def main(ctx):
    await ctx.send('pong')


# Error Handling
@client.command()
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, MemberNotFound):
        return await ctx.channel.send(embed=embed('Error', 'Du hast keinen gültigen Namen eingegeben', 10038562),
                                      delete_after=5)
    raise error


client.run(Token)
