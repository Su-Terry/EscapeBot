from core.classes import Cog_Extension
from discord.ext import commands
import json


class General(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(brief='use the given link to add this bot to your DC server')
    async def invite_link(ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        await ctx.send(jdata['invite_link'])

    @commands.command(brief='show impotant version_log')
    async def version_log(ctx):
        with open("setting.json", 'r', encoding="utf8") as jfile:
            jdata = json.load(jfile)
        with open("version.log", 'r', encoding="utf8") as file:
            txt = file.readlines()
        await ctx.send(f'目前版本: {jdata["version"]}')
        for log in txt:
            await ctx.send(log)

    # @commands.command(brief='set bot language')
    # async def lang(ctx):
    #     pass


def setup(bot):
    bot.add_cog(General(bot))
