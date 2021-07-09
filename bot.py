# encoding: utf-8
from discord.ext import commands
import os


bot = commands.Bot(command_prefix='')

bot.remove_command('help')

@bot.event
async def on_ready():
    print(">> EscapeBot is online <<")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or \
        isinstance(error, commands.TooManyArguments):
        await ctx.send('請輸入正確格式')
    if isinstance(error, commands.CommandNotFound):
        pass

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Re - Loaded {extension} done.")

for Filename in os.listdir(r'./cmds'):
    if Filename.endswith('.py'):
        bot.load_extension(f"cmds.{Filename[:-3]}")

if __name__ == '__main__':
    bot.run(os.environ['TOKEN'])
