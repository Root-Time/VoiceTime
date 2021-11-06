import asyncio

from discord import Member, Embed, ButtonStyle, Interaction, Button
from discord.ui import View

from Module.get_database import us
from Module.set_database import update_us
from Utils.embed import info
from Utils.embed import embed as _embed
from classes.button import NewButton
from classes.load_guild import LoadGuild


async def pm(member: Member, embed: Embed, view: View = None, delete_after=None):
    if not us.get(member.id, {}).get('PN', True):
        return

    guild = member.guild

    c: LoadGuild = LoadGuild(guild)

    if not view:
        view = View()

    async def pm_button(interaction: Interaction, button: Button):
        if member.id not in us.keys():
            us[member.id] = {}

        us[member.id]['PN'] = False

        update_us()

        # TODO Disable button
        await interaction.message.edit(view=view)

        await interaction.response.send_message(
            embed=_embed(c.l('Erfolgreich'), c.l('Private Benachrichtigung wurde deaktiviert!'), 'g')
        )

        await member.send(embed=info(c.l(
            'Wenn du sie wieder aktivieren willst, gehe auf einem Server und gebe `//set notification on` ein.'
        )))

    button = NewButton(c.l('Deaktiviere Benachrichtigungen'), ButtonStyle.danger, pm_button, id='pm')

    view.add_item(button)

    try:
        dm_mess = await member.send(
            embed=embed,
            view=view,
            delete_after=delete_after
        )
    except:
        return
    return
    await asyncio.sleep(30)

    for button in view.children:
        print('Last Check:', button)
        try:
            if button.id == 'pm':
                view.remove_item(button)
        except AttributeError:
            continue
    await dm_mess.edit(view=view)
