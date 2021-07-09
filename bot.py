# encoding: utf-8
from discord.ext import commands
import os, json, discord


bot = commands.Bot(command_prefix='', help_command=None)

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
async def help(ctx):
    user = ctx.author.name
    path = f'User/users/{user}.json'
    with open('setting.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
    embed = discord.Embed(title='Help for EscapeBot',
            description="逃脫遊戲: 版本{}".format(jdata['version']))
    
    embed.add_field(name='Escape', value='escape -> 進入遊戲')
    embed.add_field(name='General', value='邀請連結\n版本紀錄')
    embed.add_field(name='Administrator', value='clear {num} -> 清理訊息')
    
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        cmds = ''
        for cmd in jdata['cmds']:
            cmds += f'{cmd}\n'
        if cmds != '':
            embed.add_field(name='遊戲中指令', value=cmds)
    await ctx.send(embed=embed)

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Re - Loaded {extension} done.")

for Filename in os.listdir(r'./cmds'):
    if Filename.endswith('.py'):
        bot.load_extension(f"cmds.{Filename[:-3]}")

if __name__ == '__main__':
    bot.run(os.environ['TOKEN'])
