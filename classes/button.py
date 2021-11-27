import asyncio

from discord import ButtonStyle, Interaction
from discord.ui import Button, View

from Module.get_database import client


class NewButton(Button):
    def __init__(self, label, style: ButtonStyle = ButtonStyle.secondary, call=None, id=None, url=None):
        self.async_call = call
        super().__init__(label=label, style=style, custom_id=id, url=url)

    async def callback(self, interaction: Interaction):
        if self.async_call:
            await self.async_call(interaction, super())


def view(*args):
    _view = View()
    for button in args:
        _view.add_item(button)

    return _view


def clear_button(mess, time):
    async def temp():
        await asyncio.sleep(time)
        try:
            await mess.edit(view=View())
        except Exception as e:
            print('Line 37 Script button.py', type(e))

    client.loop.create_task(temp())
