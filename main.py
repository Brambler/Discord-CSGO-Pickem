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
version = "1.4.5"
footerVar = f"Brambles Pickem Bot - Version {version}"
discordPressence = '"Use /showpickem"'

MY_GUILD = discord.Object(id=os.getenv("discordGuildID"))  # replace with your guild id

# Function to get user's Steam ID
def get_steam_id(profile_url: str) -> Optional[str]:
    """
    Given a Steam profile URL, returns the user's 64-bit Steam ID if available.
    If the profile URL is invalid or the Steam ID is not found, returns None.
    """
    # Check if the URL is a vanity URL or a non-vanity URL
    is_vanity_url = bool(re.search(r'/id/[\w-]+', profile_url))
    is_non_vanity_url = bool(re.search(r'/profiles/\d+', profile_url))
    if not is_vanity_url and not is_non_vanity_url:
        return None

    if is_vanity_url:
        # Extract the vanity URL from the profile URL
        vanity_url = re.search(r'/id/([\w-]+)', profile_url).group(1)

        # Call the ResolveVanityURL method with the user's vanity URL
        response = requests.get(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_api_key}&vanityurl={vanity_url}')
        data = response.json()

        # Check if the request was successful and the user's SteamID was returned
        if data['response']['success'] == 1:
            return data['response']['steamid']
        else:
            return None
    else:
        # Extract the SteamID64 from the profile URL
        steam_id_64 = re.search(r'/profiles/(\d+)', profile_url).group(1)
        return steam_id_64

# Function to get user's pickem
def getPickemInfo(api_key, event, steamID, authCode, user):
    '''
    Used to get Users Pickems
    Usage: getPickemInfo(api_key, event, steamID, authCode, user)
    '''
    getTournamentLayout_url = f"https://api.steampowered.com/ICSGOTournaments_730/GetTournamentLayout/v1?key={steam_api_key}&event={event}"
    tournamentLayoutResponse = requests.get(getTournamentLayout_url)

    # tournamentVar_preliminary_stage_picks = tournamentVar_json["result"]["sections"][0]["groups"]
    # tournamentVar_quarterfinals_picks = tournamentVar_json["result"]["sections"][2]["groups"]
    # tournamentVar_semifinals_picks = tournamentVar_json["result"]["sections"][3]["groups"]
    # tournamentVar_grand_final_picks = tournamentVar_json["result"]["sections"][4]["groups"]


    tournamentVar_json = json.loads(tournamentLayoutResponse.text)
    teams_info = tournamentVar_json["result"]["teams"]

    # Define a function to get the team name by pickid
    def get_team_name_by_pickid(pickid, teams):
        for team in teams:
            if team["pickid"] == pickid:
                return team["name"]
        return None

    # Get user Predictions
    getPredictions_url = f"https://api.steampowered.com/ICSGOTournaments_730/GetTournamentPredictions/v1?key={api_key}&event={event}&steamid={steamID}&steamidkey={authCode}"

    predictions_response = requests.get(getPredictions_url)
    predictions_response_json = json.loads(predictions_response.text)

    # Access the picks from the JSON data
    current_picks = predictions_response_json["result"]["picks"]

    # create a new embed
    pickem_embed=discord.Embed(title="BLAST.tv Paris 2023 CS:GO Major Championship", description=f"{user}'s Current **Challenger Round** Picks", color=0xfffe0f)
    pickem_embed.set_author(name="SourceCode", url="https://github.com/Brambler/Discord-CSGO-Pickem", icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")

    # add fields for the 3-0 and 0-3 picks
    for pick in current_picks:
        team_name = get_team_name_by_pickid(pick['pick'], teams_info)
        if pick['index'] == 0:
            pickem_embed.add_field(name="3-0 Pick", value=team_name, inline=True)
        elif pick['index'] == 8:
            pickem_embed.add_field(name="0-3 Pick", value=team_name, inline=True)

    # add field for the to-advance picks
    to_advance_picks = ""
    for index, pick in enumerate(current_picks):
        team_name = get_team_name_by_pickid(pick['pick'], teams_info)
        if 1 <= pick['index'] <= 7:
            to_advance_picks += f"{team_name}\n"
    pickem_embed.add_field(name="To Advance Picks", value=to_advance_picks, inline=False)
    pickem_embed.set_footer(text=f'{footerVar}')
    

    return pickem_embed

# Function to retrive User Data from DB
def get_user_data(user_id):
    '''
    Retrieves User Data from Redis Database
    Usage: get_user_data(discordid)
    '''
    user_data_str = r.hget(f'{user_id}', 'user_data')
    if user_data_str:
        return json.loads(user_data_str)
    else:
        return None

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

class ReAuthConfirmationView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__(timeout=900.0)
        self.interaction = interaction

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary, emoji="✅")
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id:
            # User confirmed, proceed with re-authorization
            await interaction.response.defer(ephemeral=True)
            # Call the authorize function
            await interaction.response.send_message("Your data has been reset.", ephemeral=True)
            await authorize._callback(self.interaction)
        else:
            # User is not the one who initiated the confirmation
            await interaction.response.send_message("You are not authorized to confirm this action.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id:
            # User canceled, no further action required
            await interaction.response.send_message("Re-authorization canceled.", ephemeral=True)
        else:
            # User is not the one who initiated the confirmation
            await interaction.response.send_message("You are not authorized to cancel this action.", ephemeral=True)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event

async def on_ready():
    await client.change_presence(activity=discord.Game(discordPressence))
    print('------------------------------')
    print(f'Logged in as {client.user} (ID: {client.user.id})\nBot Version {version}\nCurrent Pressence: {discordPressence}')
    print('------------------------------')

#######################
##/authorize COMMAND###
#######################

@client.tree.command()
async def authorize(interaction: discord.Interaction):
    """Used to authorize your Steam Profile to be used with this bot."""
    # Check if the user has already authorized
    await client.change_presence(activity=discord.Game("Checking Auth"))
    print(f'Setting Pressence to "Checking Auth"')
    user_data_str = r.hget(str(interaction.user.id), 'user_data')
    if user_data_str:
        user_data = json.loads(user_data_str)
        alreadyAuthed_embed = discord.Embed(
            title='Authorization Confirmed!',
            description='You have already authorized your Steam profile.\nYou can use the **/showpickem** command.',
            color=0x00ff00
        )
        alreadyAuthed_embed.set_footer(text=f'{footerVar}')
        await client.change_presence(activity=discord.Game("Use /showpickem"))
        print(f'Setting Pressence to "Use /showpickem"')
        await interaction.response.send_message(embed=alreadyAuthed_embed, ephemeral=True)
        return

    # Create a direct message channel between the bot and the user
    authInitRespond_embed = discord.Embed(
        title='Check your DM\'s!',
        description='You have been DM\'d instructions on how to authorize your account with the bot!',
        color=0x00ff00
    )
    authInitRespond_embed.set_footer(text=f'{footerVar}')
    await interaction.response.send_message(embed=authInitRespond_embed, ephemeral=True)
    dm = await interaction.user.create_dm()


    # Send the authorization message to the user
    steamProfile_embed = discord.Embed(
        title='Enter your Steam Profile Link here',
        description='This is used to link your steamID to your Discord Account.'
                    'You can get your steam profile link by following these steps:\n\n'
                    '1. Visit [this link](https://store.steampowered.com/)\n'
                    '2. Click on your profile in the top right\n'
                    '3. Copy the URL and paste it here\n'
                    'Your url may look like: https://steamcommunity.com/id/MyBrambles/',
        color=0x2F3136
        )
    steamProfile_embed.set_footer(text=f'{footerVar}')
    await dm.send(embed=steamProfile_embed)

    def check_url(message):
        return message.author == interaction.user and message.channel == dm


    # Wait for the user to respond with their profile URL
    response_url = await client.wait_for('message', check=check_url)

    # Get the user's Steam ID from their profile URL
    steam_id_64 = get_steam_id(response_url.content)

    if steam_id_64 is not None:
        user_username = interaction.user.name
        pickemAuthCode_embed = discord.Embed(
        title='Enter Your Pick\'Em Authentication Code',
        description='You can create an authentication code for the Paris 2023 Pick\'Em Challenge by following these steps:\n\n'
                    '1. Visit [this link](https://help.steampowered.com/en/wizard/HelpWithGameIssue/?appid=730&issueid=128)\n'
                    '2. Click **2023 Paris Pick\'Em Management**\n'
                    '3. Click **Create Authentication Code**\n'
                    '4. Copy the code and paste it here in the format: `XXXX-XXXXX-XXXX`',
        color=0x2F3136
        )
        pickemAuthCode_embed.set_footer(text=f'{footerVar}')
        await dm.send(embed=pickemAuthCode_embed)
        def check_auth_code(message):
            return message.author == interaction.user and message.channel == dm

        # Wait for the user to respond with
        # Wait for the user to respond with their Pick'em auth code
        response_auth_code = await client.wait_for('message', check=check_auth_code)

        # Save the Steam ID to the Redis database
        user_data = {
            'steam_id': steam_id_64,
            'pickem_auth_code': response_auth_code.content
        }
        r.hset(str(interaction.user.id), 'user_data', json.dumps(user_data))

        # Send success message with green embed
        embed = discord.Embed(
            title='Authorization Confirmed!',
            description=f'Your Steam profile has been authorized.\nFollowing SteamID Associated with **{user_username}**: {steam_id_64}\n\nYou can now use the **/showpickem command**.\n*Thank you for authorizing!*',
            color=0x00ff00
        )
        embed.set_footer(text=f'{footerVar}')
        await client.change_presence(activity=discord.Game("Use /showpickem"))
        print(f'Setting Pressence to "Use /showpickem"')
        await dm.send(embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)

#######################
##/reauthorize COMMAND#
#######################

@client.tree.command()
async def reauthorize(interaction: discord.Interaction):
    """Used to Re-authorize your Steam Profile to be used with this bot."""

    # Check if the user has already authorized
    await client.change_presence(activity=discord.Game("Checking Auth"))
    print(f'Setting Presence to "Checking Auth"')
    user_data_str = r.hget(str(interaction.user.id), 'user_data')
    if user_data_str:
        # Ask for confirmation
        confirm_embed = discord.Embed(
            title="Confirmation",
            description="Are you sure you want to re-authorize your account? This will delete your existing data.",
            color=0xff0000
        )
        confirm_message = await interaction.channel.send(embed=confirm_embed, view=ReAuthConfirmationView(interaction))
        def check_confirm(inter):
            return inter.message.id == confirm_message.id and inter.user.id == interaction.user.id
        try:
            confirm_interaction = await client.wait_for("button_click", check=check_confirm, timeout=60)
        except asyncio.TimeoutError:
            await confirm_message.edit(content="Confirmation timed out.", view=None)
            return
        # User confirmed the action
        if confirm_interaction.component.label == "Confirm":
            # Delete the existing user data
            r.hdel(str(interaction.user.id), 'user_data')
            await confirm_message.edit(content="Your data has been deleted.")
        else:
            await confirm_message.edit(content="Action canceled.")
    else:
        NotAuthed_embed = discord.Embed(
            title='Not Authorized!',
            description='Sorry, looks like you haven\'t authorized your account yet!\nGo ahead and use the **/Authorize** command\nYou will get a DM from the bot with directions.',
            color=0xff0000
        )
        NotAuthed_embed.set_footer(text=f'{footerVar}')
        await interaction.response.send_message(embed=NotAuthed_embed, ephemeral=True)
        return


#######################
##/showpickem COMMAND##
#######################

@client.tree.command()
async def showpickem(interaction: discord.Interaction):
    """Displays the user's Pick'em information."""
    # Get the user's data from the Redis database
    user_data = get_user_data(interaction.user.id)
    if not user_data:
        embed = discord.Embed(
            title='Not Authorized!',
            description='Sorry, looks like you haven\'t authorized your account yet!\nGo ahead and use the **/Authorize** command\nYou will get a DM from the bot with directions.',
            color=0xff0000
        )
        embed.set_footer(text=f'{footerVar}')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Call the function from the other script to get the user's Pick'em information
    user_username = interaction.user.name

    await client.change_presence(activity=discord.Game(f"Retrieving Pickem for {user_username}"))
    print(f'Setting Pressence to "Retrieving Pickem for {user_username}"')
    
    pickem_info = getPickemInfo(steam_api_key, event, user_data['steam_id'], user_data['pickem_auth_code'], user_username)

    # Format the pickem_info as a string
    pickem_info_str = pickem_info

    pickemResponse_embed = discord.Embed(
            title='Pickem Retrieved!',
            description='*Only you can see this message*\n\nBelow is your pickem!\n**Your Pick\'em is now shown to everyone in this channel**\n\n*Thanks for using my bot <3*',
            color=0x00ff00
        )
    pickemResponse_embed.set_footer(text=f'{footerVar}')
    await interaction.response.send_message(embed=pickemResponse_embed, ephemeral=True)
    await client.change_presence(activity=discord.Game("Use /showpickem"))
    print(f'Setting Pressence to "Use /showpickem"')
    await interaction.channel.send(embed=pickem_info_str)

client.run(os.getenv("discordToken"))