import discord
import discord.ui
import os

version = "1.5_dev"
discordPressence = '"Use /showpickem"'
footerVar = f"Brambles Pickem Bot - Version {version}"
MY_GUILD = discord.Object(id=os.getenv("discordGuildID"))


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(discordPressence))
    print('------------------------------')
    print(f'Logged in as {client.user} (ID: {client.user.id})\nBot Version {version}\nCurrent Presence: {discordPressence}')
    print('------------------------------')


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # Create a single button with a unique custom ID
        self.button = discord.ui.Button(label="Click me!", style=discord.ButtonStyle.success, custom_id="my_button")

    async def interaction_check(self, interaction: discord.Interaction):
        # Only allow interactions from the same user who initiated the view
        return interaction.user == self.ctx.author


    async def on_timeout(self):
        # Clean up the view after it times out
        self.clear_items()

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.success, custom_id="my_button")
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)


@client.tree.command()
async def test(ctx: discord.ApplicationCommandInteraction):
    view = MyView()
    view.add_item(view.button_callback)
    await ctx.send("Please select an option:", ephemeral=True, view=view)


client.run(os.getenv("discordToken"))
