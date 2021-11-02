from datetime import datetime

import discord
from discord.ext import commands

from Utils.embed import embed
from Utils.language import language
from classes.voice_class import VoiceClass
from classes.load_guild import LoadGuild
from Module.get_database import us
from cogs.Error_Hanlder import NoData


class VoiceCreate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> VoiceTime > Join')

    @commands.Cog.listener()
    @commands.bot_has_permissions(manage_channels=True, move_members=True, manage_permissions=True, send_messages=True)
    async def on_voice_state_update(self, member: discord.Member, _, now: discord.VoiceState):
        guild: discord.Guild = member.guild
        channel: discord.VoiceChannel = now.channel
        user_setting = us.get(member.id) or {}

        if member.bot:
            return

        if not now:
            return

        # GUILD Set bot up? Are Permissions right? Are all Channel exits?
        try:
            c: LoadGuild = LoadGuild(guild, self.client)
        except:
            return

        # Language Converter
        l = lambda text: language(text, c.lang)

        if channel not in [c.normal, c.privat]:
            return

        if c.channel_cooldown(member):
            if member.voice:
                await member.move_to(None)
            try:
                await member.send(embed=embed('VoiceTime', l('Du bist auf cooldown!'), 'r'))
            except Exception:  # Forget the Error xD
                pass
            return

        c.add_channel_cooldown(member)

        privat = channel == c.privat

        # PERM False JOIN NORMAL, PRIVAT > STOP Overreaction
        await c.normal.set_permissions(member, connect=False)
        await c.normal.set_permissions(member, connect=False)

        vc: discord.VoiceChannel = await guild.create_voice_channel(
            name=f'{"Privat" if privat else "||"} {member.display_name}',
            category=c.privat.category if privat else c.normal.category
        )

        # Member disconnect before FINISH > Break

        if not member.voice:
            await vc.delete()
            await c.normal.set_permissions(member, connect=True)
            await c.normal.set_permissions(member, connect=True)
            return

        await member.move_to(vc)

        vt: VoiceClass = VoiceClass(member, vc, privat)
        await vc.set_permissions(member, connect=True, manage_channels=True)

        # CHECK Sever && User enabled CHAT?
        if c.chat and user_setting.get('chat') is not False:
            chat: discord.TextChannel = await guild.create_text_channel(
                name=f'{member.display_name}',
                category=c.setting.category
            )

            # Row is Important for Faster Handling!
            await chat.set_permissions(guild.default_role, read_messages=False)
            await chat.set_permissions(member, read_messages=True)

            pin1 = await chat.send(embed=embed(
                l('Voice Chat von {}').format(member.name),
                l('Hier kannst du mit den Leuten aus dem Voice Chat Nachrichten verschicken').format(
                    member.mention)
            ))

            pin2 = await chat.send(embed=embed(
                l('INFO'),
                l('Du kannst diesen Text Channel nur solange sehen wie du auch im jeweiligen Sprachkanal bist!'),
                'orange'
            ))

            await pin1.pin()
            await pin2.pin()

            message_content = l(
                '**{} hat den Channel um {} am {} erstellt!**\n'
            ).format(
                member.mention,
                datetime.now().strftime('%H:%M'),
                datetime.now().strftime('%m.%d')
            )

            mess = await chat.send(embed=embed('VoiceChat', message_content))

            vt.chat_id = chat.id
            vt.mess = mess
            vt.content = message_content

            # User JOIN before finish Text Channel
            if vt.queue:
                await vt.to_chat(member, True)

        # Delete Voice Channel
        if vc.members:
            await self.client.wait_for('voice_state_update', check=lambda *_: not vc.members)

        await vt.delete()


def setup(client):
    client.add_cog(VoiceCreate(client))
