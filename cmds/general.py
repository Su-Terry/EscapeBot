# encoding: utf-8
from core.classes import Cog_Extension
from discord.ext import commands
import json


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


def setup(bot):
    bot.add_cog(General(bot))
