import discord
from discord.ext import commands
import os
import challonge
import psycopg2

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))

tournament = challonge.tournaments.show(10110170)
for match in challonge.matches.index(tournament["id"]):
  if match["round"] == 1 and match["state"] == "open":
    retard = challonge.participants.show(tournament["id"], match["player1_id"])
    retard2 = challonge.participants.show(tournament["id"], match["player2_id"])
    print(retard["name"] + " " + retard2["name"])

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print('Bot is ready.')

client.run(os.getenv("DISCORD_TOKEN"))
