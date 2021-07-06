from core.classes import Cog_Extension
from discord.ext import commands
import json

with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class Administrator(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
    
    @commands.command()
    async def clear(self, ctx, num:int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=num)


def setup(bot):
    bot.add_cog(Administrator(bot))
