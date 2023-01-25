# encoding: utf-8
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(">> EscapeBot is online <<")
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or \
        isinstance(error, commands.TooManyArguments):
        await ctx.send('Wrong command format')
    if isinstance(error, commands.CommandNotFound):
        pass

async def load_extensions():
    for Filename in os.listdir(r'./cmds'):
        if Filename.endswith('.py'):
            await bot.load_extension(f"cmds.{Filename[:-3]}")

async def main():
    await load_extensions()
    await bot.start(os.getenv("BOT_TOKEN"))
    
asyncio.run(main())
