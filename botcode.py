import discord
from discord.ext import commands
from dotenv.main import load_dotenv
import os
import challonge
import psycopg2


def getDiscordID(challongename):
  i=0
  discordID=0
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT DISCORDID FROM USERSTEST WHERE CHALLONGE= %s",[challongename])
  row = cursor.fetchone()
  discordID = row[0]
  cursor.close()
  conn.close()
  return discordID

def getDelayers(round):
  lazies = []
  challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))
  tournament = challonge.tournaments.show(10110170)
  for match in challonge.matches.index(tournament["id"]):
    if match["round"] == int(round) and match["state"] == "open":
      lazies.append(challonge.participants.show(tournament["id"], match["player1_id"])["name"])
      lazies.append(challonge.participants.show(tournament["id"], match["player2_id"])["name"])
  return lazies

def main():
  load_dotenv()
  bot = commands.Bot(command_prefix = '!')
  
  @bot.event
  async def on_ready():
    print('I have logged in as {0.user}'.format(bot))

  @bot.command()
  async def pinground(ctx, round):
    i=0
    lazies = getDelayers(round)
    for lazy in lazies:
      discordID = getDiscordID(lazy)
      user = await bot.fetch_user(discordID)
      await user.send('Lenochu')
      i+=1
    await ctx.send('Poslal jsem ' + str(i) + ' zpráv.')
  bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    main()

# IMPORTANT TO DO:  Only administrator can issue commands
#                   Prepare for multiple tournaments
#                   Think deadlines through (different league systems?)
