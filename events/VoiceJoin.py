import asyncio

import discord
from discord import Guild, VoiceChannel
from discord.ext import commands
from discord_components import Button, ButtonStyle

from Module.get_database import us
from Utils.embed import voice, error, info
from Utils.language import language
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


class VoiceJoin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> VoiceTime > Join')

    @commands.Cog.listener()
    @commands.bot_has_permissions(manage_channels=True, move_members=True, manage_permissions=True, send_messages=True)
    async def on_voice_state_update(self, member: discord.Member, _, now: discord.VoiceState):
        guild: Guild = member.guild
        channel: VoiceChannel = now.channel

        # Check: Level 1
        if member.bot:
            return

        if not now:
            return

        if _ == now:
            return

        # GUILD Set bot up? Are Permissions right? Are all Channel exits?
        try:
            c: LoadGuild = LoadGuild(guild, self.client)
        except:  # TODO create own Exception NoData
            return

        # Language Converter ?? a: Why not lambda ?? Time: because its better to not use it
        def l(text: str):
            return language(text, c.lang)

        # Main Check
        if channel not in c.channels:
            return

        vt: VoiceClass = c.get_channel(channel)

        if not vt.privat:
            await vt.to_chat(member, True)
            return

        # Check: already allowed
        if member in vt.members:
            await vt.to_chat(member, True)
            return

        if member in vt.fl:
            await vt.to_chat(member, True)
            return

        # TODO Sending Warning to Owner if Admin permanent join!

        # Save Mute State ?? A: WHERE IS THE CLEAN CODE ; TIME: i need to do this!! ??
        mute = member.voice.mute

        await channel.set_permissions(member, connect=False)
        # If Queue is None >> Move to None ?? Simple ??
        print(c.queue)
        await member.move_to(c.queue)

        # Queue Things
        if c.queue and not mute:
            async def queue():
                await member.edit(mute=True)
                await self.client.wait_for('voice_state_update',
                                           check=lambda _member, last, _: member == _member and last.channel == c.queue)
                await member.edit(mute=False)

            self.client.loop.create_task(queue())

        ping_mess = await c.setting.send(vt.owner.mention)
        await ping_mess.delete()

        mess = await c.setting.send(
            embed=voice(l('Darf {} beitreten?').format(member.mention)),
            components=[
                [Button(label=l('Ja'), style=ButtonStyle.blue, id='ja'),
                 Button(label=l('Nein'), style=ButtonStyle.red, id='nein')]
            ],
            delete_after=30
        )

        # TODO convert to Async
        # Request to Owner >> Member Join?
        while True:
            try:
                event = await self.client.wait_for('button_click', check=lambda _event: _event.message == mess,
                                                   timeout=30)
            except asyncio.TimeoutError:
                # If Nobody pressed this button
                if c.queue:
                    if member in c.queue.members:
                        await member.move_to(None)

                await asyncio.sleep(1)
                if guild.get_channel(channel.id):
                    await channel.set_permissions(member, connect=True)
                return

            if event.user == vt.owner:
                await event.message.delete()
                if event.component.id == 'ja':
                    break

                if c.queue:
                    if member in c.queue.members:
                        await member.move_to(None)
                return

            if event.user == member:
                if event.component.id == 'ja':
                    await event.respond(embed=error(l('Du kannst nicht dich selbst reinlassen?')))
                    continue
                await mess.delete()

                if c.queue:
                    if member in c.queue.members:
                        await member.move_to(None)

                await event.respond(
                    embed=voice(l('In dem du auf Nein gedrückt hast, hast du die Anfrage abgebrochen!')))
                return

            await event.respond(embed=error(l('Du bist nicht berechtigt diesen Knopf zu klicken!')))

        vt.add(member)
        await vt.to_chat(member, True)

        if c.queue:
            if member in c.queue.members and guild.get_channel(channel.id):
                await member.move_to(channel)
                return

        # Direct Message > Member
        if not us.get(member.id, {}).get('PN', True):
            print('Debug')
            return

        link = await channel.create_invite(max_age=300)
        try:
            dm_mess = await member.send(
                embed=voice(l(
                    '**{}**\n'
                    'Du kannst nun den Channel {} von {} beitreten'
                ).format(guild.name, channel.mention, vt.owner.mention)),
                components=[
                    [Button(label=l('Beitreten'), style=ButtonStyle.URL, url=str(link), id='2'),
                     Button(label=l('Deaktiviere Benachrichtigung'), style=ButtonStyle.blue)]
                ],
                delete_after=300
            )
        except:  # TODO find the Error Name
            return

        while True:
            try:
                event = await self.client.wait_for('button_click', check=lambda _event: _event.message == dm_mess, timeout=30)
                await event.respond(type=6)
            except asyncio.TimeoutError:
                await dm_mess.edit(
                    components=[
                        [Button(label=l('beitreten'), style=ButtonStyle.blue, id='1'),
                         Button(label=l('Deaktiviere Benachrichtigung'), style=ButtonStyle.URL, url=str(link), id='2', disabled=True)]
                    ]
                )
                return
            await dm_mess.delete()
            break

        if member.id not in us.keys():
            us[member.id] = {}

        us[member.id]['PN'] = False

        await member.send(embed=voice(l(
            'Private Benachrichtigung wurde deaktiviert!'), 'green'
        ))

        await member.send(embed=info(l(
            'Wenn du sie wieder aktivieren willst, gehe auf einem Server und gebe `//set notification on` ein.'
        )))


def setup(client):
    client.add_cog(VoiceJoin(client))
