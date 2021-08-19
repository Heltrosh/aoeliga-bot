import asyncio
from json import dump
import discord
from discord.ext import commands
from dotenv.main import load_dotenv
import os
import challonge
import psycopg2


def getRows():
  i=0
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT CHALLONGE, DISCORDID, EXCUSED FROM EXCUSETEST")
  rows = cursor.fetchall()
  cursor.close()
  conn.close()
  if rows:
    return rows

def getDelayers(round, leagueid):
  lazies = []
  challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))
  tournaments = [challonge.tournaments.show(10110170)]
  for match in challonge.matches.index(tournaments[leagueid]["id"]):
    if match["round"] == int(round) and match["state"] == "open":
      lazies.append(challonge.participants.show(tournaments[leagueid]["id"], match["player1_id"])["name"])
      lazies.append(challonge.participants.show(tournaments[leagueid]["id"], match["player2_id"])["name"])
  return lazies

def processExcuse(challonge, rounds):
  cmdRounds = [int(round) for round in rounds]
  newRounds = []
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT CHALLONGE, EXCUSED FROM EXCUSETEST WHERE CHALLONGE = %s", [challonge])
  row = cursor.fetchone()
  if not row:
    cursor.close()
    conn.close()
    return newRounds
  dbRounds = row[1] #for clarity
  if not dbRounds:
    newRounds = sorted(cmdRounds)
  else:
    newRounds = sorted((set(cmdRounds).symmetric_difference(set(dbRounds))))
  cursor.execute("UPDATE EXCUSETEST SET EXCUSED = %s WHERE CHALLONGE = %s", (newRounds, challonge))
  cursor.close()
  conn.commit()
  conn.close()
  return newRounds
  
def checkExcused(round, excuses):
  if not excuses:
    return False
  for excuse in excuses:
    if excuse == int(round):
      return True
  return False

def getPingMessage(discordName, round):
  conn = conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT DEADLINE FROM DEADLINES WHERE ROUND = %s", [round])
  row = cursor.fetchone()
  cursor.close()
  conn.close()
  deadline = row[0]
  messageStr = f"""Ahoj {discordName}, 
píšeme ti, lebo nám chýba výsledok tvojho ligového zápasu:
  
KOLO: {round}.
PROTIVNÍK: [CHALLONGEACC, DISCORDACC PLACEHOLDER]
DEADLINE: {deadline}

Po odohratí zápasu musí byť jeho výsledok nahlásený najneskôr do dátumu deadlinu.
Zápasy s nenahlásenými výsledkami sú automaticky kontumované Adminom.
**V prípade ak zápas nie je možné odohrať načas, kontaktuj Admina Ligy [KapEr#1695] so žiadosťou o predĺženie deadlinu.**
  
VÝSLEDOK SA NAHLASUJE NA DVOCH MIESTACH:
1) AOEliga Discord Server
2) **Challonge Bracket**
[URL NA BRACKET PLACEHOLDER]"""
  return messageStr

def main():
  load_dotenv()
  intents = discord.Intents.default()
  intents.members = True
  bot = commands.Bot(command_prefix = '!', intents=intents)
  
  @bot.event
  async def on_ready():
    print('I have logged in as {0.user}'.format(bot))
#COMMANDS
  @bot.command()
  async def pinground(ctx, round, league):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Mě může používat jenom KapEr, co to zkoušíš!")
    else:
      i=0
      lazies = getDelayers(round, (int(league)-1))
      dbRows = getRows()
      ignorants = []
      notFound = []
      excusedList = []
      excusedAmount = 0
      for lazy in lazies:
        discordID = 0
        found = False
        excused = False
        for row in dbRows:
          if row[0] == lazy:
            if checkExcused(round, row[2]):
              excused = True
              excusedAmount += 1
              excusedList.append(lazy)
            found = True
            discordID = row[1]
        if found and not excused:
          try:
            user = await bot.fetch_user(discordID)
          except:
            notFound.append(lazy)
            continue
          try:
            pingMessage = getPingMessage(user.name, round)
            await user.send(pingMessage)
            i+=1
          except discord.Forbidden:
            ignorants.append(lazy)
        elif not found:
          notFound.append(lazy)
      if ignorants:
        ignorantstr = "Zprávu jsem nedoručil: "
        for ignorant in ignorants:
          ignorantstr += (ignorant + ' ') 
        await ctx.send(ignorantstr)
      if notFound:
        notFoundstr = 'Nenalezl jsem v databázi/na discordu: '
        for nf in notFound:
          notFoundstr += (nf + ' ')
        await ctx.send(notFoundstr)
      if excusedList:
        excusedStr = ' ('
        for ex in excusedList:
          if ex == excusedList[-1]:
            excusedStr += ex
          else:
            excusedStr += (ex + ', ')
        excusedStr += ') '
        await ctx.send('Poslal jsem ' + str(i) + ' zpráv. ' + str(excusedAmount) + ' hráčů' + excusedStr + 'bylo omluvených.')
      else:
        await ctx.send('Poslal jsem ' + str(i) + ' zpráv.')

  @bot.command()
  async def excuse(ctx, *args):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Mě může používat jenom KapEr, co to zkoušíš!")
    else:
      if args[0] == 'list':
        excuseListOutput = ''
        dbRows = getRows()
        for row in dbRows:
          if row[2]:
            rounds = ', '.join([str(round) for round in row[2]])
            excuseListOutput += (row[0] + ': ' + rounds + '\n')
        if excuseListOutput:
          await ctx.send(excuseListOutput)
      elif len(args) == 1:
        dbRows = getRows()
        for row in dbRows:
          if row[0] == args[0]:
            if row[2]:
              rounds = ', '.join([str(round) for round in row[2]])
              await ctx.send(row[0] + ' je omluvený z kol: ' + rounds + '.')
              return
            else:
              await ctx.send(row[0] + ' není omluvený z žádného kola.')
              return
        await ctx.send('Nenalezl jsem hráče ' + args[0] + ' v databázi.')
      elif len(args) > 1:
        for arg in args[1:]:
          if not arg.isnumeric():
            await ctx.send('Kola nebyla správně zadaná, použij !help excuse pro správnou syntax.')
        resultRounds = processExcuse(args[0], args[1:])
        if not resultRounds:
          await ctx.send('Nenalezl jsem hráče ' + args[0] + ' v databázi.')
        else:
          rounds = ', '.join([str(round) for round in resultRounds])
          await ctx.send('Nový seznam omluvených kol hráče ' + args[0] + ': ' + rounds + '.')



#COG MANAGEMENT
  @bot.command()
  async def load(ctx, extension):
    if extension == 'dmall' and ctx.author.id == 164698420777320448:
      bot.load_extension(f'cogs.{extension}')
    elif not extension == 'dmall':
      bot.load_extension(f'cogs.{extension}')
  @bot.command()
  async def unload(ctx, extension):
    if extension == 'dmall' and ctx.author.id == 164698420777320448:
      bot.unload_extension(f'cogs.{extension}')
    elif not extension == 'dmall':
      bot.unload_extension(f'cogs.{extension}')
  
  bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    main()

# IMPORTANT TO DO:  1) Add deadlines
#                   2) Help command stuff
#                   3) Sanitize input data !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
