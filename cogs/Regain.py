import json

from discord.ext import commands

from Module.set_database import delete_voice_backup
from classes.voice_class import VoiceClass


class Regain(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        with open('Data/voice.json', 'r') as f:
            voices = json.load(f)

        for voice in voices.values():
            guild = self.client.get_guild(voice.get('guild'))
            owner = guild.get_member(voice.get('owner'))
            vc_id = voice.get('id')
            privat = voice.get('privat')
            vc = guild.get_channel(vc_id)
            chat = guild.get_channel(voice.get('chat'))
            if not vc:
                delete_voice_backup(vc_id)
                if chat:
                    await chat.delete()
                continue
            vt: VoiceClass = VoiceClass(owner, vc, privat)

            if chat:
                mess = await chat.fetch_message(voice.get('mess'))
                content = voice.get('content')
                date = voice.get('date')
                vt.recreate(chat, mess, content, date)

            async def delete():
                if vc.members:
                    await self.client.wait_for('voice_state_update', check=lambda *_: not vc.members)

                await vt.delete()

            delete_voice_backup(vc_id)
            self.client.loop.create_task(delete())

        print('Module >>> Regain')


def setup(client):
    client.add_cog(Regain(client))
