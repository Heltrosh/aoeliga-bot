import os

import discord
from discord.ext import commands
from dotenv.main import load_dotenv

from mods.consts import *

def main():
    load_dotenv()
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix = "!", intents=intents)
    
    @bot.event
    async def on_ready():
        print("I have logged in as {0.user}".format(bot))

    @bot.event
    async def on_message(message): 
        # Currently used to resend DMs sent to the bot to me
        if message.guild is None and message.author != bot.user and message.author.id != HELTROSH_DISCORD_ID:
            user = await bot.fetch_user(HELTROSH_DISCORD_ID)
            resendMessage = "From: " + message.author.name + "\n" + "Content: " + message.content
            await user.send(resendMessage)
        await bot.process_commands(message)

#COG MANAGEMENT
    @bot.command()
    async def load(ctx, extension):
        if extension == "dmall" and ctx.author.id == HELTROSH_DISCORD_ID:
            bot.load_extension(f"cogs.{extension}")
    @bot.command()
    async def unload(ctx, extension):
        if extension == "dmall" and ctx.author.id == HELTROSH_DISCORD_ID:
            bot.unload_extension(f"cogs.{extension}")
     
    bot.load_extension("mods.cogs.pinground")
    bot.load_extension("mods.cogs.excuse")
    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
        main()
