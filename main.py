import discord
import discord.ui
import os

client = discord.Client()

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.select = discord.ui.Select(
            placeholder="Choose a Flavor!",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Vanilla",
                    description="Pick this if you like vanilla!"
                ),
                discord.SelectOption(
                    label="Chocolate",
                    description="Pick this if you like chocolate!"
                ),
                discord.SelectOption(
                    label="Strawberry",
                    description="Pick this if you like strawberry!"
                )
            ]
        )
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction):
        # Only allow interactions from the same user who initiated the view
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        # Clean up the view after it times out
        self.clear_items()

    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!", ephemeral=True)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.application_command()
async def flavor(ctx: discord.ApplicationCommandInteraction):
    view = MyView()
    view.ctx = ctx
    await ctx.send("Choose a flavor!", view=view)


client.run(os.getenv("discordToken"))
