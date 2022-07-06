from discord.ext import commands

from modules.consts import *
from modules.functions import getPlayers, excuseList, excusePlayer

class Excuse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def excuse(self, ctx, *args):
       # Used for excusing players so they don't get message telling them to play their match when they excused themselves
        if not (ctx.author.id == KAPER_DISCORD_ID or ctx.author.id == HELTROSH_DISCORD_ID):
            await ctx.send(ADMIN_ONLY_ERROR)
            return       
        if args[0] == "list":
            excuseListOutput = excuseList()
            await ctx.send(excuseListOutput)
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
            await ctx.send(f"Nenalezl jsem hráče {args[0]} v databázi.")
        elif len(args) > 1:
            for arg in args[1:]:
                if not arg.isnumeric():
                    await ctx.send(EXCUSE_ROUNDS_SYNTAX)
                    return
                elif not (1 <= int(arg) <= 9):
                    await ctx.send(EXCUSE_ROUNDS_BOUNDARY)
                    return
            resultRounds = excusePlayer(args[0], args[1:])
            if not resultRounds:
                await ctx.send(f"Nenalezl jsem hráče {args[0]} v databázi.")
            elif resultRounds == -1:
                await ctx.send(f"Nový seznam omluvených kol hráče {args[0]}: žádná.")
            else:
                rounds = ", ".join([str(round) for round in resultRounds])
                await ctx.send(f"Nový seznam omluvených kol hráče {args[0]}: {rounds}.") 

def setup(bot):
    bot.add_cog(Excuse(bot))