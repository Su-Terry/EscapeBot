from discord.ext.commands.core import has_permissions
from core.classes import Cog_Extension
from discord.ext import commands
import json

with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class Administrator(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
    
    @has_permissions(manage_messages=True)
    @commands.command(brief='Clear {num} messages, "clear {num}"')
    async def clear(self, ctx, num:int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=num)


async def setup(bot):
    await bot.add_cog(Administrator(bot))
