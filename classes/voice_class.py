from datetime import datetime

import discord
from discord import Member, Guild, TextChannel

from Module.set_database import create_voice_backup, update_voice_backup
from Utils.embed import embed
from Utils.language import language
from classes.load_guild import LoadGuild
from Module.get_database import voice, fl


class VoiceClass:
    def __init__(self, owner, vc: discord.VoiceChannel, privat: bool):
        self.id = vc.id
        self.owner: Member = owner
        self.guild: Guild = owner.guild
        self.privat = privat

        # Chat
        self.queue = []
        self.chat = None
        self.mess = None
        self.content = None
        self.date = None

        self.members = {owner}

        self.c: LoadGuild = LoadGuild(self.guild)
        self.lang = self.c.lang

        voice.setdefault(self.guild.id, []).append(self)
        self.create_backup()
        # TODO save Class __DICT__ to DATABASE

    def rem(self, member):
        self.members.remove(member)

    def add(self, member):
        self.members.add(member)

    # Voice Channel Join Leave Message
    async def to_chat(self, member: discord.Member, type: bool):
        if not self.chat:
            self.queue.append(member)
            return
        context = self.l('ist beigetreten') if type else self.l('hat verlassen')
        await self.chat.set_permissions(member, view_channel=True)

        await self().set_permissions(member, connect=True)
        is_owner = '**(owner)**' if member == self.owner else ''

        last_message = await self.chat.fetch_message(self.chat.last_message_id)
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
            message = await self.chat.send(embed=embed('VoiceChat', mess))
            self.mess = message
            return

        await last_message.edit(embed=embed('VoiceChat', str(mess)))

    def l(self, text):
        return language(text, self.lang)

    def recreate(self, chat, mess, content, date):
        self.chat = chat
        self.mess = mess
        self.content = content
        self.date = date

    def create_backup(self):
        save_dict = self.__dict__.copy()
        save_dict['owner'] = self.owner.id
        # save_dict['guild'] = self.guild.id
        save_dict['members'] = [member.id for member in self.members]
        print(save_dict['owner'])

        delete_keys = []
        for key, value in save_dict.items():
            if '_' in key or key in ['c', 'queue', 'date']:  # TODO Queue Need Check later
                delete_keys.append(key)
                continue
            if type(value) not in [str, int, bool, type(None), list]:
                save_dict[key] = value.id

        for key in delete_keys:
            del save_dict[key]

        if self.chat:
            save_dict['chat'] = self.chat.id
        if self.mess:
            save_dict['mess'] = self.mess.id

        create_voice_backup(self.id, save_dict)

    def update_backup(self, update_param, value):
        if type(value) not in [str, int, bool, type(None)]:
            value = value.id
        update_voice_backup(self.id, update_param, value)

    async def delete(self, type=False):
        if self.chat:
            await self.chat.delete()

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

    @property
    def chat(self):
        return self._chat

    @chat.setter
    def chat(self, chat):
        self._chat = chat
        self.update_backup('chat', chat)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner
        self.update_backup('owner', owner)

    @property
    def mess(self):
        return self._mess

    @mess.setter
    def mess(self, mess):
        self._mess = mess
        self.update_backup('mess', mess)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content
        self.update_backup('content', content)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date
        self.update_backup('date', date)
