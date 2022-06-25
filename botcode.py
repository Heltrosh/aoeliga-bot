import asyncio
from email import message
from json import dump
import discord
from discord.ext import commands
from discord.message import Attachment
from dotenv.main import load_dotenv
import os
import challonge
import psycopg2


def getPlayers():
  i=0
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT CHALLONGE, DISCORDID, EXCUSED, LEAGUE FROM PLAYERS")
  rows = cursor.fetchall()
  cursor.close()
  conn.close()
  if rows:
    return rows

def getDelayers(round, leagueid):
  lazies = []
  challRound = 0
  if round < 8:
    challRound = round
  elif round == 8:
    challRound = 1
  else:
    challRound = 2
  
  challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))
  tournaments = [challonge.tournaments.show('3deg6sfm'), challonge.tournaments.show('6svp9be5'), challonge.tournaments.show('ldc7iv9i'), challonge.tournaments.show('wgmwco9o'), challonge.tournaments.show('szwgkw9x'), challonge.tournaments.show('9ha7dixz')]
  for match in challonge.matches.index(tournaments[leagueid]["id"]):
    if match["round"] == challRound and match["state"] == "open":
      if round < 8: #group stage
        for player in challonge.participants.index(tournaments[leagueid]["id"]):
          if player["group_player_ids"][0] == match["player1_id"]:
            lazies.append([])
            lazies[-1].append(player["challonge_username"])
            for opponent in challonge.participants.index(tournaments[leagueid]["id"]):
              if opponent["group_player_ids"][0] == match["player2_id"]:
                lazies[-1].append(opponent["challonge_username"])
            lazies.append([])
            lazies[-1].append(lazies[-2][1])
            lazies[-1].append(lazies[-2][0])
      else: #playoffs
        lazies.append([])
        lazies[-1].append(challonge.participants.show(tournaments[leagueid]["id"], match["player1_id"])["challonge_username"])
        lazies[-1].append(challonge.participants.show(tournaments[leagueid]["id"], match["player2_id"])["challonge_username"])
        lazies.append([])
        lazies[-1].append(lazies[-2][1])
        lazies[-1].append(lazies[-2][0])
  return lazies

def processExcuse(challonge, rounds):
  cmdRounds = [int(round) for round in rounds]
  newRounds = []
  conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT CHALLONGE, EXCUSED FROM PLAYERS WHERE CHALLONGE = %s", [challonge])
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
  cursor.execute("UPDATE PLAYERS SET EXCUSED = %s WHERE CHALLONGE = %s", (newRounds, challonge))
  cursor.close()
  conn.commit()
  conn.close()
  if not newRounds:
    return -1
  return newRounds
  
def checkExcused(round, excuses):
  if not excuses:
    return False
  for excuse in excuses:
    if excuse == int(round):
      return True
  return False

def getPingMessage(discordName, round, opponent, league, isOpponentExcused):
  conn = conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
  cursor = conn.cursor()
  cursor.execute("SELECT DEADLINE FROM DEADLINES WHERE ROUND = %s", [round])
  row = cursor.fetchone()
  deadline = row[0]
  cursor.execute("SELECT DISCORDNAME FROM PLAYERS WHERE CHALLONGE = %s", [opponent])
  row = cursor.fetchone()
  opponentDiscord = "ERROR, CONTACT HELTROSH"
  if row:
    opponentDiscord = row[0] 
  cursor.execute("SELECT LINK, CHANNEL FROM BRACKETLINKS WHERE LEAGUE = %s", [league])
  row = cursor.fetchone()
  bracketURL = row[0]
  discordChannel = row[1]
  cursor.close()
  conn.close()
  if isOpponentExcused:
    messageStr = f"""Ahoj {discordName},
píšeme ti, lebo nám chýba výsledok tvojho ligového zápasu:
KOLO: {round}.
PROTIVNÍK: {opponent}, {opponentDiscord}

Tvoj zápas sa v tomto týždni nedá odohrať.
Tvoj protivník bol pridaný na listinu dočasne ospravedlnených hráčov -
<#886902603479412736>.

Medzičasom môžeš toto kolo preskočiť a hrať niektoré iné. Aktuálne kolo sa dohrá keď protivník bude znovu k dispozícií."""
  
  else:
    messageStr = f"""Ahoj {discordName}, 
píšeme ti, lebo nám chýba výsledok tvojho ligového zápasu:
  
KOLO: {round}.
PROTIVNÍK: {opponent}, {opponentDiscord}
DEADLINE: {deadline}

Po odohratí zápasu musí byť jeho výsledok nahlásený najneskôr do dátumu deadlinu.
Zápasy s nenahlásenými výsledkami sú automaticky kontumované Adminom.
**V prípade ak zápas nie je možné odohrať načas, kontaktuj Admina Ligy [KapEr#1695] so žiadosťou o predĺženie deadlinu.**
  
VÝSLEDOK SA NAHLASUJE NA DVOCH MIESTACH:
1) AOEliga Discord Server
<#{discordChannel}>
2) **Challonge Bracket**
<{bracketURL}>"""
  return messageStr

def pingInputCheck(round, league):
  if ((1 <= league <= 6) and (1 <= int(round) <= 9)): 
    return True
  else:
    return False

def main():
  load_dotenv()
  intents = discord.Intents.default()
  intents.members = True
  bot = commands.Bot(command_prefix = '!', intents=intents)
  
  @bot.event
  async def on_ready():
    print('I have logged in as {0.user}'.format(bot))

  @bot.event
  async def on_message(message):
    if message.guild is None and message.author != bot.user and message.author.id != 164698420777320448:
      user = await bot.fetch_user(164698420777320448)
      resendMessage = 'From: ' + message.author.name + '\n' + 'Content: ' + message.content
      await user.send(resendMessage)
    await bot.process_commands(message)

#COMMANDS
  @bot.command()
  async def pinground(ctx, round, league):
    if not (ctx.author.id == 687276408057233658 or ctx.author.id == 164698420777320448):
      await ctx.send("Mě může používat jenom KapEr, co to zkoušíš!")
    elif not (round.isnumeric() and league.isnumeric() and pingInputCheck(int(round), int(league))):
      await ctx.send('Špatně zadané kolo/liga. Kolo musí být celé číslo v intervalu 1-9 a liga musí být celé číslo v intervalu 1-6.')
    else:
      i=0
      lazies = getDelayers(int(round), (int(league)-1))
      dbRows = getPlayers()
      ignorants = []
      notFound = []
      excusedList = []
      excusedAmount = 0
      for lazyList in lazies:
        lazy = lazyList[0]
        opponent = lazyList[1]
        discordID = 0
        found = False
        excused = False
        isOpponentExcused = False
        for row in dbRows:
          if row[0] == lazy:
            if checkExcused(round, row[2]):
              excused = True
              excusedAmount += 1
              excusedList.append(lazy)
            found = True
            discordID = row[1]
          elif row[0] == opponent:
            if checkExcused(round, row[2]):
              isOpponentExcused = True
        if found and not excused:
          try:
            user = await bot.fetch_user(discordID)
          except:
            notFound.append(lazy)
            continue
          try:
            pingMessage = getPingMessage(user.name, round, opponent, league, isOpponentExcused)
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
    if not (ctx.author.id == 687276408057233658 or ctx.author.id == 164698420777320448):
      await ctx.send("Mě může používat jenom KapEr, co to zkoušíš!")
    else:
      if args[0] == 'list':
        excuseListOutput = '**ZOZNAM OSPRAVEDLNENÝCH HRÁČOV**\n'
        leaguePrinted = [0, 0, 0, 0, 0, 0]
        firstLeague = True
        dbRows = getPlayers()
        sortedDbRows = sorted(dbRows, key=lambda x: x[3])
        for row in sortedDbRows:
          if row[2]:
            if leaguePrinted[row[3]-1] == 0:
              if firstLeague:
                excuseListOutput += ( '**' + str(row[3]) + '. LIGA:**\n')
                firstLeague = False
              else:
                excuseListOutput += ( '\n**' + str(row[3]) + '. LIGA:**\n')
              leaguePrinted[row[3]] = 1
            excuseListOutput += ('CHALLONGE: ' + row[0] + ', OSPRAVEDLNENÉ KOLÁ: ')
            rounds = ', '.join([str(round) for round in row[2]])
            excuseListOutput += (rounds + '\n')
        if excuseListOutput:
          await ctx.send(excuseListOutput)
        else:
          await ctx.send('Žádní omluvení hráči.')
      elif len(args) == 1:
        dbRows = getPlayers()
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
            await ctx.send('Kola nebyla správně zadaná. Podívej se do dokumentace na správnou syntax.')
            return  
          elif arg.isnumeric() and int(arg) > 9:
            await ctx.send('Některé zadané kolo bylo vyšší číslo, než je množství kol, zadej kola <= 9.')
            return
        resultRounds = processExcuse(args[0], args[1:])
        if not resultRounds:
          await ctx.send('Nenalezl jsem hráče ' + args[0] + ' v databázi.')
        elif resultRounds == -1:
          await ctx.send('Nový seznam omluvených kol hráče: žádná.')
        else:
          rounds = ', '.join([str(round) for round in resultRounds])
          await ctx.send('Nový seznam omluvených kol hráče ' + args[0] + ': ' + rounds + '.')
          
#COG MANAGEMENT
  @bot.command()
  async def load(ctx, extension):
    if extension == 'dmall' and ctx.author.id == 164698420777320448:
      bot.load_extension(f'cogs.{extension}')
    elif extension == 'usercommands' and ctx.author.id == 164698420777320448 or ctx.author.id == 687276408057233658:
      bot.load_extension(f'cogs.{extension}')
    elif not extension == 'dmall' or 'usercommands':
      bot.load_extension(f'cogs.{extension}')
  @bot.command()
  async def unload(ctx, extension):
    if extension == 'dmall' and ctx.author.id == 164698420777320448:
      bot.unload_extension(f'cogs.{extension}')
    elif extension == 'usercommands' and ctx.author.id == 164698420777320448 or ctx.author.id == 687276408057233658:
      bot.unload_extension(f'cogs.{extension}')
    elif not extension == 'dmall' or 'usercommands':
      bot.unload_extension(f'cogs.{extension}')
  
  
  #bot.load_extension('cogs.usercommands')
  bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
