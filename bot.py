from discord.ext import commands
import json, os


bot = commands.Bot(command_prefix='%')

@bot.event
async def on_ready():
    print(">> EscapeBot is online <<")

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Re - Loaded {extension} done.")

for Filename in os.listdir(r'./cmds'):
    if Filename.endswith('.py'):
        bot.load_extension(f"cmds.{Filename[:-3]}")

if __name__ == '__main__':
    with open("setting.json", 'r', encoding="utf8") as jfile:
        jdata = json.load(jfile)
    bot.run(os.environ['TOKEN'])
