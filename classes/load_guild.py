import asyncio

import discord
from discord import Guild, Member, Client

from Module.creating_permission import create_channel
from Utils.embed import embed
from Utils.language import language
from Module.get_database import ss, temp_guild, voice, client
from cogs.Error_Hanlder import NoData


class LoadGuild:
    def __init__(self, guild: Guild):

        self.ss = ss.get(guild.id)
        if not ss:
            raise Exception('NoData')
        self.guild = guild
        self.client: Client = client

        # Possible NULL :: Check if exits
        self.config = self._get_ss('config', False)
        self.queue = self._get_ss('queue', False)

        # Get IMPORTANT Channel
        self.normal = self._get_ss('normal')
        self.privat = self._get_ss('privat')
        self.logs = self._get_ss('logs')
        self.setting = self._get_ss('setting')

        self.chat = self.ss['chat']

        self.lang = self.ss['lang']
        self.friend = self.ss['friends']

        # Setting
        self.claim_time = self.ss.get('claim_time')

        # Temp Data
        self.voice = voice.setdefault(self.guild.id, [])
        self.channels = [vt() for vt in self.voice]

        if guild.id not in temp_guild.keys():
            temp_guild[guild.id] = {'cooldown': []}

        self.temp = temp_guild.get(guild.id)

        self.create_channel_cooldown = self.temp.get('cooldown')

    def get_channel(self, voice_channel):
        if isinstance(voice_channel, discord.VoiceChannel):
            for vt in self.voice:
                if voice_channel == vt() or voice_channel == vt.owner:
                    return vt

        # Shorter //Note Maybe use Later
        # return (vt for vt in self.voice if voice_channel == vt())

    def add_channel_cooldown(self, member):
        if not self.client:
            return

        self.create_channel_cooldown.append(member)

        async def timer():
            await asyncio.sleep(3)
            if member not in self.create_channel_cooldown:
                return
            self.create_channel_cooldown.remove(member)

        self.client.loop.create_task(timer())

    def channel_cooldown(self, member: Member) -> bool:
        """
        Member
        Check if Member can create a new Channel
        """
        return member in self.create_channel_cooldown

    def l(self, text):
        return language(text, self.lang)

    # Get Channel // CHECK if Exits
    def _get_ss(self, name, must_exits=True):
        channel = self.guild.get_channel(self.ss[name])

        if not must_exits:
            return

        if not channel:
            self.channel_error(name)
            raise NoData()

        return channel

    def channel_error(self, name):
        async def async_channel_error():
            if self.config:
                return

            channel = await create_channel(self, 'VOICETIME-CONFIG', 'text')

            if not channel:
                return

            await channel.send(embed=embed(
                self.l('Warnung!!!'),
                self.l(
                    f'Es existiert kein {name} Channel\n'
                    'Bitte benutzte diesen Command //set normal'),
                'o'
            ))

        if self.client:
            self.client.loop.create_task(async_channel_error())
