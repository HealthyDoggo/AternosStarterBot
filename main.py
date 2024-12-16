import os
import discord
from dotenv import load_dotenv
from startserverundetected import startingServer, get_player_names
load_dotenv()
import os
import discord
from discord import app_commands   
import time
# load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('SERVER_ID')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
        name="start", 
        description="starts the Aternos server if not already on.",
        guild=discord.Object(id=int(SERVER))
)
async def start_server(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        timeTaken = startingServer(True)
        if timeTaken:
            await interaction.followup.send(f'Server started in {timeTaken} seconds')
        else:
            await interaction.followup.send('Error: server already running')
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occurred. Please try again.")
# @tree.command(
#         name="uptime",
#         description="note: only works when server started by bot.",
#         guild=discord.Object(id=int(SERVER))
# )
# async def show_time(interaction: discord.Interaction):
#     try:
#         await interaction.response.defer()
#         serveroff = startingServer(False)
#         if serveroff:
#             await  interaction.followup.send('The Server is currently offline',  ephemeral=True)
#         else:
#             await interaction.followup.send(f'The server has been on for {time.gmtime(timeStarted-time.time())}')
#     except:
#         await interaction.followup.send("An error occured. Please try again.")
@tree.command(
        name="status",
        description="displays the current status of the aternos server.",
        guild=discord.Object(id=int(SERVER))
)
async def checkStatus(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        if startingServer(False) == False:
            await interaction.followup.send('The server is currently on', ephemeral=True)
        else:
            await interaction.followup.send('The server is currently off', ephemeral=True)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occurred. Please try again.")
@tree.command(
        name="online",
        description="Displays the players currently online on the server.",
        guild=discord.Object(id=int(SERVER))
)
async def displayOnlinePlayers(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        result = ", ".join([item for item in get_player_names()])
        if result:
            await interaction.followup.send(f'{result} are currently online.')
        elif startingServer(False):
            await interaction.followup.send('No one is currently online, but the server is on! quick, quick, quick!')
        else:
            await interaction.followup.send("No one is currently online as the server is off.")
    except Exception as e:
        print(e)
        await interaction.followup.send(f"An error occurred. Please try again. {e}")
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=int(SERVER)))
    print("ready!")

client.run(TOKEN)