from discord.ext import commands
import json, os

with open("setting.json", 'r', encoding="utf8") as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix='%')

@bot.event
async def on_ready():
    print(">> EscapeBot is online <<")

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Re - Loaded {extension} done.")

@bot.command()
async def get_link(ctx):
    await ctx.channel.send(jdata['invite_link'])

for Filename in os.listdir(r'./cmds'):
    if Filename.endswith('.py'):
        bot.load_extension(f"cmds.{Filename[:-3]}")

if __name__ == '__main__':
    bot.run(jdata['TOKEN'])
