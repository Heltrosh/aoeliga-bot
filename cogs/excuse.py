import sys
sys.path.insert(0,'..')

from discord.ext import commands

import consts
from functions import getPlayers, processExcuse

class Excuse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def excuse(self, ctx, *args):
       # Used for excusing players so they don't get message telling them to play their match when they excused themselves
        if not (ctx.author.id == consts.KAPER_DISCORD_ID or ctx.author.id == consts.HELTROSH_DISCORD_ID):
            await ctx.send(consts.ADMIN_ONLY_ERROR)
            return       
        if args[0] == "list":
            excuseListOutput = "**ZOZNAM OSPRAVEDLNENÝCH HRÁČOV**\n"
            leaguePrinted = [0, 0, 0, 0, 0, 0]
            firstLeague = True
            players = getPlayers()
            sortedPlayers = sorted(players, key=lambda x: x[3])
            for player in sortedPlayers:
                if player[2]:
                    if leaguePrinted[player[3]-1] == 0:
                        if firstLeague:
                            excuseListOutput += ( "**" + str(player[3]) + ". LIGA:**\n")
                            firstLeague = False
                        else:
                            excuseListOutput += ( "\n**" + str(player[3]) + ". LIGA:**\n")
                        leaguePrinted[player[3]-1] = 1
                    excuseListOutput += ("CHALLONGE: " + player[0] + ", OSPRAVEDLNENÉ KOLÁ: ")
                    rounds = ", ".join([str(round) for round in player[2]])
                    excuseListOutput += (rounds + "\n")
            if excuseListOutput:
                await ctx.send(excuseListOutput)
            else:
                await ctx.send("Žádní omluvení hráči.")
        elif len(args) == 1:
            players = getPlayers()
            for player in players:
                if player[0] == args[0]:
                    if player[2]:
                        rounds = ", ".join([str(round) for round in player[2]])
                        await ctx.send(player[0] + " je omluvený z kol: " + rounds + ".")
                        return
                    else:
                        await ctx.send(player[0] + " není omluvený z žádného kola.")
                        return
            await ctx.send("Nenalezl jsem hráče " + args[0] + " v databázi.")
        elif len(args) > 1:
            for arg in args[1:]:
                if not arg.isnumeric():
                    await ctx.send("Kola nebyla správně zadaná. Podívej se do dokumentace na správnou syntax.")
                    return
                elif arg.isnumeric() and int(arg) > 9:
                    await ctx.send("Některé zadané kolo bylo vyšší číslo, než je množství kol, zadej kola <= 9.")
                    return
            resultRounds = processExcuse(args[0], args[1:])
            if not resultRounds:
                await ctx.send("Nenalezl jsem hráče " + args[0] + " v databázi.")
            elif resultRounds == -1:
                await ctx.send("Nový seznam omluvených kol hráče: žádná.")
            else:
                rounds = ", ".join([str(round) for round in resultRounds])
                await ctx.send("Nový seznam omluvených kol hráče " + args[0] + ": " + rounds + ".") 

def setup(bot):
    bot.add_cog(Excuse(bot))