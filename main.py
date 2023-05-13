import discord
import discord.ui
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

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Option 1", custom_id="option1", style=discord.ButtonStyle.primary)
    async def option1_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Option 1 selected", ephemeral=True)

    @discord.ui.button(label="Option 2", custom_id="option2", style=discord.ButtonStyle.primary)
    async def option2_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Option 2 selected", ephemeral=True)

    @discord.ui.button(label="Option 3", custom_id="option3", style=discord.ButtonStyle.primary)
    async def option3_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Option 3 selected", ephemeral=True)


intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(discordPressence))
    print('------------------------------')
    print(f'Logged in as {client.user} (ID: {client.user.id})\nBot Version {version}\nCurrent Pressence: {discordPressence}')
    print('------------------------------')


# Multiple Choice
async def test(interaction: discord.Interaction):
    """Used to test a multiplechoice command"""
    await interaction.response.send_message("Please select an option:", ephemeral=True, view=MyView())

client.run(os.getenv("discordToken"))