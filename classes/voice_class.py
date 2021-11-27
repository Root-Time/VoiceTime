import asyncio
from datetime import datetime, timedelta

import discord
from discord import Member, Guild, ButtonStyle, Interaction, Button

from Module.set_database import create_voice_backup, update_voice_backup
from Utils.embed import embed, vc_embed
from Utils.language import language
from classes.button import view, NewButton
from classes.load_guild import LoadGuild
from Module.get_database import voice, owner_vc_list, client


class VoiceClass:
    def __init__(self, owner, vc: discord.VoiceChannel, privat: bool):
        self.claim_mess = None
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
        self.claim_cooldown = None

        self.c: LoadGuild = LoadGuild(self.guild)
        self.lang = self.c.lang

        voice.setdefault(self.guild.id, []).append(self)
        self.create_backup()
        owner_vc_list.setdefault(owner.id, []).append(self)
        # TODO save Class __DICT__ to DATABASE

    def remove(self, member):
        self.members.remove(member)
        self.remove_chat(member)

    def add(self, member):
        self.members.add(member)

    def disconnect(self, member: Member = None):
        """
        Owner or Member disconnect
        """

        if member == self.owner:
            self.disconnect_chat(member)

            async def wait():
                await asyncio.sleep(self.c.claim_time)
                await self.send_claim_message()
            client.loop.create_task(wait())
            return

        self.remove(member)

    async def send_claim_message(self):
        """
        Coroutine
        Send the claiming Message
        """

        async def claim_button(interaction: Interaction, button: Button):
            if not interaction.user.voice:
                await interaction.response.send_message(
                    self.l('Du musst in einem Channel sein um ihn zu claimen!'), ephemeral=True
                )
                return
            if interaction.user not in self.members or interaction.user.voice.channel != self():
                await interaction.response.send_message(
                    self.l('Du musst in diesen Channel sein um ihn zu claimen!'), ephemeral=True)
                return

            self.owner = interaction.user

            self.claim_mess.edit(
                embed=vc_embed(
                    self.l('{}\nDu bist nun der neue Owner vom Channel {}')
                        .format(interaction.user.mention, self().mention)
                ), view=None
            )

        channel = self.chat or self.c.setting
        self.claim_mess = await channel.send(
            embed=vc_embed(self.l('{}\n ist nun zu claimen').format(self().mention)),
            view=view(
                NewButton('claim', ButtonStyle.primary, claim_button)
            )
        )

    # Claiming
    def owner_disconnect(self):
        print('Wurde ausgelöst')
        self.claim_cooldown = datetime.now() + timedelta(seconds=300)  # Todo Timedelta to Serverside

        # Claim > Button Event 
        async def wait():
            await asyncio.sleep(300)
            if not self.claim_cooldown:
                return

            async def claim_button(interaction: Interaction, _):
                if not interaction.user.voice:
                    await interaction.response.send_message(
                        self.l('Du musst in einem Channel sein um ihn zu claimen!'), ephemeral=True)
                    return
                if interaction.user not in self.members or interaction.user.voice.channel != self():
                    await interaction.response.send_message(
                        self.l('Du musst in diesen Channel sein um ihn zu claimen!'), ephemeral=True)
                    return

                # Change Owner
                owner_vc_list.get(self.owner).remove(self)

                self.owner = interaction.user
                await self.claim_mess.edit(
                    embed=vc_embed(
                        self.l('{}\nDu bist nun der neue Owner vom Channel {}')
                            .format(interaction.user.mention, self().mention)
                    ), view=None
                )
                # TODO Add More Function

            self.claim_mess = await self.c.setting.send(
                embed=vc_embed(self.l('{}\n ist nun zu claimen').format(self().mention)),
                view=view(
                    NewButton('claim', ButtonStyle.primary, claim_button)
                )
            )

        client.loop.create_task(wait())

    def owner_join(self):
        self.claim_cooldown = None

    def remove_chat(self, member):
        """
        Remove And Disable Chat for Member
        """
        self.disconnect_chat(member)

        if self.chat:
            client.loop.create_task(self.chat.set_permissions(member, view=False))

    def add_chat(self, member):
        """
        Add and Enable Chat for Member
        """
        self.connect_chat(member)

        if self.chat:
            client.loop.create_task(self.chat.set_permissions(member, view=False))

    def connect_chat(self, member):
        self.to_chat(member, True)

    def disconnect_chat(self, member):
        self.to_chat(member, False)

    # Voice Channel Join Leave Message
    async def to_chat(self, member: discord.Member, type: bool):
        if not self.chat:
            self.queue.append(member)
            return
        context = self.l('ist beigetreten') if type else self.l('hat verlassen')

        await self().set_permissions(member, connect=True)
        is_owner = '**(owner)**' if member == self.owner else ''

        if self.chat.last_message_id:
            last_message = await self.chat.fetch_message(self.chat.last_message_id)
        else:
            last_message = '_'  # Unknown Bug Fix
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

    # Recreate CHAT After Crash!
    def recreate(self, chat, mess, content, date):
        self.chat = chat
        self.mess = mess
        self.content = content
        self.date = date

    # Create Backup to get Channel back
    def create_backup(self):
        save_dict = self.__dict__.copy()
        save_dict['owner'] = self.owner.id
        # save_dict['guild'] = self.guild.id
        save_dict['members'] = [member.id for member in self.members]

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
        if self in owner_vc_list.get(self.owner, []):
            owner_vc_list.get(self.owner).remove(self)

        if self.guild.get_channel(self.chat.id):
            await self.chat.delete()

        if self.claim_mess:
            await self.claim_mess.delete()

        # Delete from Voice Entry
        if self in voice.get(self.guild.id, []):
            voice[self.guild.id].remove(self)

        # IMPORTANT CHECK DON'T COMBINE OR DELETE
        if type:
            return

        if self():
            await self().delete()

    def __call__(self):
        vc: discord.VoiceChannel = self.guild.get_channel(self.id)
        if not vc:
            client.loop.create_task(self.delete(True))
        return vc

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
