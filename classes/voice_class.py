from datetime import datetime

import discord
from discord import Member, Guild, TextChannel

from Utils.embed import embed
from Utils.language import language
from classes.load_guild import LoadGuild
from Module.get_database import voice, fl


class VoiceClass:
    def __init__(self, owner, vc: discord.VoiceChannel, privat: bool):
        self.owner: Member = owner
        self.guild: Guild = owner.guild
        self.id = vc.id
        self.privat = privat

        # Chat
        self.queue = []
        self.chat_id = None
        self.mess = None
        self.content = None
        self.date = None
        self.fl = fl.get(owner.id) or []

        self.members = {owner}

        self.c: LoadGuild = LoadGuild(self.guild)
        self.lang = self.c.lang

        voice.setdefault(self.guild.id, []).append(self)
        # TODO save Class __DICT__ to DATABASE

    def chat(self) -> TextChannel:
        return self.guild.get_channel(self.chat_id)

    def rem(self, member):
        self.members.remove(member)

    def add(self, member):
        self.members.add(member)

    # Voice Channel Join Leave Message
    async def to_chat(self, member: discord.Member, type: bool):
        if not self.chat():
            return
        context = self.l('ist beigetreten') if type else self.l('hat verlassen')
        await self.chat().set_permissions(member, view_channel=True)

        await self().set_permissions(member, connect=True)
        is_owner = '**(owner)**' if member == self.owner else ''

        last_message = await self.chat().fetch_message(self.chat().last_message_id)
        date_time = datetime.now().strftime('%m.%d - %H:%M')
        if self.date == date_time:
            date = ''
        else:
            date = f'\n**{date_time}**'
            self.date = date_time

        mess = self.content + f'{date}\n> {member.mention} {is_owner} {context}!'

        self.content = mess
        if last_message != self.mess:
            await self.mess.delete()
            message = await self.chat().send(embed=embed('VoiceChat', mess))
            self.mess = message
            return

        await last_message.edit(embed=embed('VoiceChat', str(mess)))

    def l(self, text):
        return language(text, self.lang)

    async def delete(self, type=False):
        if self.chat():
            await self.chat().delete()

        # Delete from Voice Entry
        if self in voice.get(self.guild.id, []):
            voice[self.guild.id].remove(self)

        # IMPORTANT CHECK DON'T COMBINE OR DELETE
        if type:
            return

        if self():
            await self().delete()

    def __call__(self):
        return self.guild.get_channel(self.id) or self.delete(True)
