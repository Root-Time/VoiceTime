import discord
from discord import Guild, VoiceChannel
from discord.ext import commands

from Utils.language import language
from classes.load_guild import LoadGuild
from Module.get_database import us
from classes.voice_class import VoiceClass


class VoiceLeave(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> VoiceTime > Leave')

    @commands.Cog.listener()
    @commands.bot_has_permissions(manage_channels=True, move_members=True, manage_permissions=True, send_messages=True)
    async def on_voice_state_update(self, member: discord.Member, last: discord.VoiceState, _now):
        # Check
        if not last:
            return

        if last == _now:
            return

        guild: Guild = member.guild
        channel: VoiceChannel = last.channel
        user_setting = us.get(member.id) or {}

        # GUILD Set bot up? Are Permissions right? Are all Channel exits?
        try:
            c: LoadGuild = LoadGuild(guild)
        except:
            return

        # Language Converter
        l = lambda text: language(text, c.lang)

        if channel not in c.channels:
            return

        if not channel.members:
            return

        vt: VoiceClass = c.get_channel(channel)

        if member not in vt.members:
            return
        await vt.to_chat(member, False)





def setup(client):
    client.add_cog(VoiceLeave(client))
