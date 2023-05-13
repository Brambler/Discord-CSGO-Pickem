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
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        
    async def setup_hook(self):
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

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.success)
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)

@client.tree.command()
async def test(interaction: discord.Interaction):
    view = MyView()
    view.add_item(view.button_callback)
    await interaction.response.send_message("Please select an option:", ephemeral=True, view=view)


client.run(os.getenv("discordToken"))
