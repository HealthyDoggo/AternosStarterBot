import os
import discord
from dotenv import load_dotenv
from test import get_logs, get_correct_ips, get_player_names, starting_server, add_ip_address, get_console, maintain_server_tab, maintain_players_tab
load_dotenv()
import os
import discord
from discord import app_commands
import time
import asyncio
from helpers import save_pending_responses, save_linked_accounts, save_correct_ip_addresses, load_pending_responses, load_linked_accounts, load_correct_ip_addresses


TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('SERVER_ID')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
pending_responses = list(load_pending_responses())
linked_accounts = load_linked_accounts()


console_queue = asyncio.Queue()
print("output testing")
async def handle_player_response(message: discord.Message, address):
    if message.content.lower() == 'yes':
        await message.author.send(f"Thank you for confirming. Your login from IP {address} is authorised.")
        MCusername = [username for username, discord_id in linked_accounts.items() if discord_id == message.author.id][0]
        add_ip_address(MCusername, address)
        await console_queue.put({"action": "command", "text": f"pardon-ip {address}"})
        print(pending_responses)
        pending_responses.remove([message.author.id, address])
    elif message.content.lower() == 'no':
        await message.author.send(f"Thank you. The login attempt from IP {address} has been blocked and the IP banned.")
        pending_responses.remove([message.author.id, address])
    else:
        await message.author.send("This was an invalid response. Please reply with 'yes' or 'no'.")
    save_pending_responses(pending_responses)
@tree.command(
        name="start", 
        description="starts the Aternos server if not already on.",
        guild=discord.Object(id=int(SERVER))
)
async def start_server(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        timeTaken = await starting_server(True)
        if timeTaken:
            await interaction.followup.send(f'Server started in {timeTaken} seconds')
        else:
            await interaction.followup.send('Error: server already running')
    except Exception as e:
        print(f"Error in start server main function: {e}")
        await interaction.followup.send("An error occurred. Please try again.\n {e}")
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
        if await starting_server(False):
            await interaction.followup.send('The server is currently on', ephemeral=True)
        else:
            await interaction.followup.send('The server is currently off', ephemeral=True)
    except Exception as e:
        print(f"Error in check status main function: {e}")
        await interaction.followup.send("An error occurred. Please try again.\n {e}")
@tree.command(
        name="online",
        description="Displays the players currently online on the server.",
        guild=discord.Object(id=int(SERVER))
)
async def displayOnlinePlayers(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        result = ", ".join([item for item in await get_player_names()])
        if result:
            await interaction.followup.send(f'{result} are currently online.')
        elif await starting_server(False):
            await interaction.followup.send('No one is currently online, but the server is on! quick, quick, quick!')
        else:
            await interaction.followup.send("No one is currently online as the server is off.")
    except Exception as e:
        print(f"Error in display online players main function: {e}")
        await interaction.followup.send(f"An error occurred. Please try again. \n {e}")
@tree.command(
        name="link",
        description="Connects this discord account to your minecraft account.",
        guild=discord.Object(id=int(SERVER))
)
async def link(interaction: discord.Interaction, username: str):
    if interaction.user.id in list(linked_accounts.values()):
        await interaction.response.send_message("Sorry, this discord account is linked to another minecraft account. Please use /unlink to disconnect them.")
    elif username.lower() in list(linked_accounts.keys()):
        await interaction.response.send_message("Sorry, this minecraft account is linked to another discord account. If you think this is incorrect, please DM me immediately.")
    else:
        linked_accounts[username.lower()] = interaction.user.id
        await interaction.response.send_message(f"Account {username} successfully linked to discord.")
    save_linked_accounts(linked_accounts)
@tree.command(
        name="unlink",
        description="Disconnect this discord account from its connected minecraft account.",
        guild=discord.Object(id=int(SERVER))
)
async def unlink(interaction: discord.Interaction):
    if interaction.user.id in list(linked_accounts.values()):
        MCusername = [username for username, discord_id in linked_accounts.items() if discord_id == interaction.user.id][0]
        del linked_accounts[MCusername]
        save_linked_accounts(linked_accounts)
        await interaction.response.send_message(f"Account {MCusername} successfully disconnected from discord.")
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await tree.sync(guild=discord.Object(id=int(SERVER)))
    asyncio.create_task(maintain_server_tab())
    await asyncio.sleep(7)
    asyncio.create_task(maintain_players_tab())
    await asyncio.sleep(7)
    asyncio.create_task(get_console(console_queue, client, pending_responses, linked_accounts))
@client.event
async def on_message(message: discord.Message):
    if message.guild is None and not message.author.bot:
        for id, address in pending_responses:
            if message.author.id == id and address in message.reference.resolved.content:
                await handle_player_response(message, address)
if __name__ == "__main__":
    try:             
        client.run(TOKEN)
    except KeyboardInterrupt:
        # Handle manual stop with Ctrl+C or similar
        save_pending_responses(pending_responses)
        save_linked_accounts(linked_accounts)
        save_correct_ip_addresses(get_correct_ips())
        print("Bot stopped and data saved.")
    except Exception as e:
        # Handle unexpected exceptions (if needed)
        print(f"An error occurred: {e}")
        save_pending_responses(pending_responses)
        save_linked_accounts(linked_accounts)
        save_correct_ip_addresses(get_correct_ips())
        print("Unexpected error occurred, data saved.")