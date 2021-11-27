import discord
from discord import Guild, VoiceChannel, ButtonStyle, Interaction, Button
from discord.ext import commands
from discord.ui import View

from Module.get_database import fl
from Module.privat_message import pm
from Utils.embed import voice, error
from Utils.language import language
from classes.button import NewButton, view
from classes.load_guild import LoadGuild
from classes.voice_class import VoiceClass


# noinspection PyTypeChecker
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
        if not now:
            return

        if _.channel == now.channel:
            return

        # GUILD Set bot up? Are Permissions right? Are all Channel exits?
        try:
            c: LoadGuild = LoadGuild(guild)
        except:  # TODO create own Exception NoData
            return

        # Language Converter ?? a: Why not lambda ?? Time: because its better to not use it
        def l(text: str):
            return language(text, c.lang)

        # Main Check
        if channel not in c.channels:
            return

        vt: VoiceClass = c.get_channel(channel)
        if not vt.privat or member.bot:
            vt.add(member)
            await vt.to_chat(member, True)
            return

        # Check: already allowed
        if member in vt.members:
            if member == vt.owner:
                vt.owner_join()
            await vt.to_chat(member, True)
            return

        if member.id in fl.get(vt.owner.id, []):
            vt.add(member)
            await vt.to_chat(member, True)
            return

        # TODO Sending Warning to Owner if Admin permanent join!

        # Save Mute State ?? A: WHERE IS THE CLEAN CODE ; TIME: i need to do this!! ??
        mute = member.voice.mute

        await channel.set_permissions(member, connect=False)
        # If Queue is None >> Move to None ?? Simple ??
        await member.move_to(c.queue)

        # Queue Things
        if c.queue and not mute:
            async def queue():
                await member.edit(mute=True)
                await self.client.wait_for('voice_state_update',
                                           check=lambda _member, last, _: member == _member and last.channel == c.queue)
                await member.edit(mute=False)

            self.client.loop.create_task(queue())

        # Send Joining Message
        ping_mess = await c.setting.send(vt.owner.mention)
        await ping_mess.delete()

        # noinspection PyTypeChecker
        async def join_request_button(interaction: Interaction, button: Button):
            if interaction.user == vt.owner:
                await interaction.message.delete()
                if button.label == 'ja':
                    vt.add(member)
                    await channel.set_permissions(member, connect=True)

                    if c.queue:
                        if member in c.queue.members and guild.get_channel(channel.id):
                            await member.move_to(channel)
                            return

                    link = await channel.create_invite(max_age=300)

                    embed = voice(l(
                        '**{}**\n'
                        'Du kannst nun den Channel {} von {} beitreten'
                    ).format(guild.name, channel.mention, vt.owner.mention))

                    pm_view = view(
                        NewButton(l('Beitreten'), ButtonStyle.url, url=str(link))
                    )
                    await pm(member, embed, pm_view)

                # Action >> Nein
                if c.queue:
                    if member in c.queue.members:
                        await member.move_to(None)
                return

            if interaction.user == member:
                if button.label == 'ja':
                    await interaction.response.send_message(
                        embed=error(l('Du kannst    nicht dich selbst reinlassen?')),
                        ephemeral=True,
                        delete_after=10
                    )
                    return

                await mess.delete()

                if c.queue:
                    if member in c.queue.members:
                        await member.move_to(None)

                await interaction.response.send_message(
                    embed=voice(l('In dem du auf Nein gedrückt hast, hast du die Anfrage abgebrochen!')),
                    ephemeral=True,
                    delete_after=10
                )
                return

            await interaction.response.send_message(
                embed=error(l('Du bist nicht berechtigt diesen Knopf zu klicken!')),
                ephemeral=True,
                delete_after=10
            )

        mess = await c.setting.send(
            embed=voice(l('Darf {} beitreten?').format(member.mention)),
            view=view(
                NewButton(l('ja'), ButtonStyle.primary, join_request_button),
                NewButton(l('Nein'), ButtonStyle.danger, join_request_button)
            ),
            delete_after=30
        )


def setup(_client):
    _client.add_cog(VoiceJoin(_client))
