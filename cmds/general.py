# encoding: utf-8
from core.classes import Cog_Extension
from discord.ext import commands
import os, json, discord


class General(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(brief='add this bot to your DC server')
    async def 邀請連結(self, ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        await ctx.send(jdata['invite_link'])

    @commands.command()
    async def 版本紀錄(self, ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        with open("version.log", 'r', encoding="utf8") as file:
            txt = file.readlines()
        await ctx.send(f'目前版本: {jdata["version"]}')
        for log in txt:
            await ctx.send(log)

    @commands.command()
    async def help(ctx):
        user = ctx.author.name
        path = f'User/users/{user}.json'
        with open('setting.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        embed = discord.Embed(title='Help for EscapeBot',
            description="文字版逃脫遊戲: 版本{}".format(jdata['version']))
        
        embed.add_field(name='Escape', value='`escape`: 進入遊戲', inline=False)
        embed.add_field(name='General', value='`邀請連結`  `版本紀錄`', inline=False)
        embed.add_field(name='Administrator', value='`clear {num}`: 清理{num}則訊息', inline=False)
        
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
            if jdata['inGame'] == 'TRUE':
                cmds = ''
                for cmd in jdata['cmds']:
                    cmds += f'`{cmd}`  '
                if cmds != '':
                    embed.add_field(name='遊戲中指令', value=cmds, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
