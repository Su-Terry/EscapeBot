from discord.ext import commands
import os

bot = commands.Bot(command_prefix='')

@bot.event
async def on_ready():
    print(">> EscapeCmdsBot is online <<")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('請輸入正確格式')

@bot.commands()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Re - Loaded {extension} done.")

for filename in os.listdir('./cmds'):
    if filename.startswith('game') and filename.endswith('.py'):
        bot.load_extension(f"cmds.{filename[:-3]}")

if __name__ == '__main__':
    bot.run(os.environ['TOKEN2'])