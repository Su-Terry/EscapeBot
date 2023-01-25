# encoding: utf-8
from core.classes import Cog_Extension
from discord.ext import commands
import os, json, discord


class General(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(brief='add this bot to your DC server')
    async def invite_link(self, ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        await ctx.send(jdata['invite_link'])

    @commands.command()
    async def version_log(self, ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        with open("version.log", 'r', encoding="utf8") as file:
            txt = file.readlines()
        await ctx.send(f'Current version: {jdata["version"]}')
        for log in txt:
            await ctx.send(log)

    @commands.command()
    async def help(self, ctx):
        """Customize -- The help command for EscapeBot"""
        user = ctx.author.name
        path = f'User/users/{user}.json'
        with open('setting.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        embed = discord.Embed(title='Help for EscapeBot',
            description="Text Adventure: Version{}".format(jdata['version']))
        
        embed.add_field(name='Escape', value='`escape`: start game', inline=False)
        embed.add_field(name='General', value='`invite_link`  `version_log`', inline=False)
        embed.add_field(name='Administrator', value='`clear {num}`: Clear {num} messages', inline=False)
        
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
            if jdata['inGame'] == 'TRUE':
                cmds = ''
                for cmd in jdata['cmds']:
                    cmds += f'`{cmd}`  '
                if cmds != '':
                    embed.add_field(name='Cmds in Game', value=cmds, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
