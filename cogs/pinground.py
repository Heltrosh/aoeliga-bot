import sys
sys.path.insert(0,'..')


import discord
from discord.ext import commands

import consts
from functions import getPlayers, getDelayers, getPingMessage, pingInputCheck

class PingRound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pinground(self, ctx, round, league):
        # The main command of the bot - sends DMs to players with unreported results
        if not (ctx.author.id == consts.KAPER_DISCORD_ID or ctx.author.id == consts.HELTROSH_DISCORD_ID):
            await ctx.send(consts.ADMIN_ONLY_ERROR)
            return
        elif not (round.isnumeric() and league.isnumeric() and (1 <= league <= 6) and (1 <= round <= 9)):
            await ctx.send(consts.WRONG_ROUND_OR_LEAGUE)
            return
        i=0
        lazies = getDelayers(int(round), (int(league)-1))
        players = getPlayers()
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
            for player in players:
                if player[0] == lazy:
                    if player[2] and round in player[2]:
                        excused = True
                        excusedAmount += 1
                        excusedList.append(lazy)
                    found = True
                    discordID = player[1]
                elif player[0] == opponent:
                    if player[2] and round in player[2]:
                        isOpponentExcused = True
            if found and not excused:
                try:
                    user = await self.bot.fetch_user(discordID)
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
                ignorantstr += (ignorant + " ") 
            await ctx.send(ignorantstr)
        if notFound:
            notFoundstr = "Nenalezl jsem v databázi/na discordu: "
            for nf in notFound:
                notFoundstr += (nf + " ")
            await ctx.send(notFoundstr)
        if excusedList:
            excusedStr = " ("
            for ex in excusedList:
                if ex == excusedList[-1]:
                    excusedStr += ex
                else:
                    excusedStr += (ex + ", ")
            excusedStr += ") "
            await ctx.send("Poslal jsem " + str(i) + " zpráv. " + str(excusedAmount) + " hráčů" + excusedStr + "bylo omluvených.")
        else:
            await ctx.send("Poslal jsem " + str(i) + " zpráv.")

def setup(bot):
    bot.add_cog(PingRound(bot))