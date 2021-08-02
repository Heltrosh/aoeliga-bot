import discord
from discord.ext import commands
import os
import challonge
import psycopg2

def getDiscordName(challongename):
  print('Cnameinserted:' + challongename)
  i=0
  discordName=""
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT DISCORD FROM USERS WHERE CHALLONGE= %s",[challongename])
  rows = cursor.fetchall()
  for row in rows:
    discordName = row[0]
  print('Dnameret:' + discordName)
  cursor.close()
  conn.close()
  return discordName

def getDelayers(round):
  print('roundinserted:' + round)
  challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))
  tournament = challonge.tournaments.show(10110170)
  for match in challonge.matches.index(tournament["id"]):
   if match["round"] == round and match["state"] == "open":
     retard = challonge.participants.show(tournament["id"], match["player2_id"])
     return retard["name"]

client = commands.Bot(command_prefix = '!')
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.command()
async def delayerlist(ctx, round):
  delayerName = getDelayers(round)
  print(delayerName)
  discordName = getDiscordName(delayerName)
  print(discordName)
  await ctx.send(discordName)

client.run(os.getenv("DISCORD_TOKEN"))
