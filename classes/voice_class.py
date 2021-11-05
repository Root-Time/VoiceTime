from datetime import datetime

import discord
from discord import Member, Guild, TextChannel

from Utils.embed import embed
from Utils.language import language
from classes.load_guild import LoadGuild
from Module.get_database import voice, fl, saved_voice


class VoiceClass:
    def __init__(self, owner, vc: discord.VoiceChannel, privat: bool):
        self.owner: Member = owner
        self.guild: Guild = owner.guild
        self.id = vc.id
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
        self.save()
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

    def save(self):
        save_dict = self.__dict__.copy()
        save_dict['owner'] = self.owner.id
        save_dict['guild'] = self.guild.id
        save_dict['members'] = [member.id for member in self.members]
        del save_dict['c']
        del save_dict['queue']  # TODO Need Check later
        if self.chat:
            save_dict['chat'] = self.chat.id
            if self.mess.id:
                save_dict['mess'] = self.mess.id

        saved_voice(self.id, save_dict)

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
        self.save()
        self._chat = chat

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self.save()
        self._owner = owner

    @property
    def mess(self):
        return self._mess

    @mess.setter
    def mess(self, mess):
        self.save()
        self._mess = mess

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self.save()
        self._content = content

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self.save()
        self._date = date
