import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print('Bot is ready.')

client.run('ODcxNDU3ODMwMjExODQyMTA4.YQbmWQ.NlYHeaBTQ7j4ewMYY_zkYSFG8fg')
