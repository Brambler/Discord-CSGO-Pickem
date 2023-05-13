import discord
import json
import re
import requests
import asyncio
import os
import redis
from redis.commands.json.path import Path
from typing import Optional
from discord import app_commands

r = redis.from_url(os.environ.get("REDISCLOUD_URL"))
steam_api_key = os.getenv("steam_api_key")
event = os.getenv("event_id")
version = "1.5_dev"
footerVar = f"Brambles Pickem Bot - Version {version}"
discordPressence = '"Use /showpickem"'

MY_GUILD = discord.Object(id=os.getenv("discordGuildID"))  # replace with your guild id

class MyClient(discord.Client):
    '''
    A CommandTree is a special type that holds all the application command
    state required to make it work. This is a separate class because it
    allows all the extra state to be opt-in.
    Whenever you want to work with application commands, your tree is used
    to store and work with them.
    Note: When using commands.Bot instead of discord.Client, the bot will
    maintain its own tree instead.
    '''
    def __init__(self, *, intents: discord.Intents):
        '''
        In this basic example, we just synchronize the app commands to one guild.
        Instead of specifying a guild to every command, we copy over our global commands instead.
        By doing so, we don't have to wait up to an hour until they are shown to the end-user.
        '''
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(discordPressence))
    print('------------------------------')
    print(f'Logged in as {client.user} (ID: {client.user.id})\nBot Version {version}\nCurrent Pressence: {discordPressence}')
    print('------------------------------')


# Multiple Choice
@client.tree.command()
async def test(interaction: discord.Interaction):
    """Used to test a multiple choice command"""
    options = [
        {
            "label": "Option 1",
            "value": "option1"
        },
        {
            "label": "Option 2",
            "value": "option2"
        },
        {
            "label": "Option 3",
            "value": "option3"
        }
    ]
    # Create a select menu with the options
    select_menu = discord.ui.SelectMenu(custom_id="test_select_menu", options=options)
    # Create an action row with the select menu
    action_row = discord.ui.ActionRow(select_menu)

    # Send a message with the select menu
    embed = discord.Embed(
        title='Authorization Confirmed!',
        description=f'Testing Message',
        color=0x00ff00
    )
    embed.set_footer(text=f'{footerVar}')
    await client.change_presence(activity=discord.Game("Use /showpickem"))
    await interaction.response.send_message(embed=embed, ephemeral=True, components=[action_row])

    # Wait for the user's selection
    try:
        select_ctx: discord.ui.SelectContext = await client.wait_for("select_option", check=lambda ctx: ctx.component.custom_id == "test_select_menu" and ctx.user.id == interaction.user.id, timeout=30)
        selected_option = select_ctx.values[0]
        await select_ctx.send(f"You selected: {selected_option}", ephemeral=True)
    except asyncio.TimeoutError:
        await interaction.followup.send("You didn't make a selection.", ephemeral=True)

client.run(os.getenv("discordToken"))