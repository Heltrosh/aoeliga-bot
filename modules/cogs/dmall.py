import asyncio

from discord.ext import commands

from modules.consts import *

class DMAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dmall(self, ctx, *, message:str):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(ADMIN_ONLY_ERROR)
            return
        sent = 0
        for member in ctx.guild.members:
            try:
                await member.send(message)
                sent += 1
                if sent % 30 == 0:
                    asyncio.sleep(60)
            except: 
                pass
        await ctx.send('Poslal jsem ' + str(sent) + ' zpráv.')

def setup(bot):
    bot.add_cog(DMAll(bot))