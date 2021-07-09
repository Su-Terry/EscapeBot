# encoding: utf-8
from discord.ext import commands
from core.classes import Cog_Extension
from cmds.escape import Escape
import os, json

async def inGame(ctx):
    user = ctx.author.name
    path = f'User/users/{user}.json'
    if not os.path.isfile(path): return False
    with open(path, 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
        if jdata['inGame'] == 'FALSE':
            return False
    return True

async def hintInCmds(ctx):
    user = ctx.author.name
    with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
    return '提示' in jdata['cmds']

async def mvInCmds(ctx):
    user = ctx.author.name
    with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
    return 'mv' in jdata['cmds']

async def gotoInCmds(ctx):
    user = ctx.author.name
    with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
    return 'goto' in jdata['cmds']

async def checkInCmds(ctx):
    user = ctx.author.name
    with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)
    return '檢查' in jdata['cmds']

class Cmds(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        global escape
        escape = Escape(bot)

    @commands.check(inGame)
    @commands.check(hintInCmds)
    @commands.command(brief='查看遊戲提示, "HINT"')
    async def 提示(self, msg) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        await msg.channel.send(jdata['hint'][int(jdata['room_plot_idx'])])
        await msg.channel.send('請注意: 這一關的密室逃脫提示還沒寫完整，敬請期待')

    @commands.check(inGame)
    @commands.check(mvInCmds)
    @commands.command(brief='把[object]移動到[place], "mv [object] [place]"')
    async def mv(self, msg, object:str, place:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if 'mv' not in jdata['cmds']: return
        if object not in jdata['objects']:
            await msg.channel.send('移動失敗，這可能不是物品或目前還未出現')
            return
        if place not in jdata['positions'] + jdata['rooms']:
            await msg.channel.send('移動失敗，目的地不是一個能合法移動到的地方')
            return
        if object not in jdata[f'{jdata["room_at"]}_object']:
            await msg.channel.send('移動失敗，這個物品不在你的房間裡, 你只能移動你房間的物品')
            return
        if object in jdata[f'{jdata[place]}_object']:
            await msg.channel.send(f'移動失敗，[{object}]已經在[{place}]了')
            return
        jdata[f'{place}_object'].append(object)
        for i in jdata['positions']+jdata['rooms']:
            if object in jdata[i]:
                jdata[i].remove(object)
                await msg.channel.send(f'已將[{object}]從[{i}]移動到[{place}]')
        plots = escape.getCmdPlot(f'mv {object} {place}_plot', user)
        for plot in plots:
            await msg.channel.send(plot)
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

    @commands.check(inGame)
    @commands.check(gotoInCmds)
    @commands.command(brief='移動到[place], "goto {place}"')
    async def goto(self, msg, place:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if 'goto' not in jdata['cmds']: return
        if place == jdata['at']:
            await msg.channel.send('移動失敗，你已經在這裡了，You are sleeping')
        if place in jdata['positions']:
            jdata['at'] = place
            await msg.channel.send(f'已移動至[{place}]!')
            plots = escape.getCmdPlot(f'goto {place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
        elif place in jdata['rooms']:
            jdata['at'] = jdata['room_at'] = place
            await msg.channel.send(f'已移動至[{place}]!')
            plots = escape.getCmdPlot(f'{place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
            await msg.channel.send(embed=escape.getRoomEmbed(user))
        else:
            await msg.channel.send('移動失敗，這可能不是一個能移動到的地方或目前還未出現')
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

    @commands.check(inGame)
    @commands.check(checkInCmds)
    @commands.command(brief='獲得劇情中在[]/()內名字的劇情, "檢查 [房間/位置/物件]/(附件)"')
    async def 檢查(self, msg, name:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if '檢查' not in jdata['cmds']: return
        jdata['inInputPasswd'] = ''
        
        attachment_name = f'{jdata["inCheck"]}_{name}'
        if attachment_name in jdata['attachments']:
            jdata["inCheck"] = attachment_name
            if attachment_name in jdata["lock"]:
                lock_status = jdata[f'{attachment_name}_status']
                plots = jdata[f'{attachment_name}_{lock_status}_plot']
                if lock_status == 'lock':
                    jdata['inInputPasswd'] = attachment_name
                    await msg.channel.send("輸入x或命令取消輸入模式")
            else:
                plots = jdata[f'{attachment_name}_plot']
        elif name in jdata['rooms']+jdata['positions']+jdata['objects']:
            # if name in jdata['positions']:
            #     exect_name = f"{jdata['room_at']}_position"
            # pass
            jdata['inCheck'] = name
            plots = jdata[f'{name}_plot']
        else:
            await msg.channel.send('目前你在的地方沒有這個地方/東西')
            return

        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

        escape.addItem(plots, user)
        for plot in plots:
            await msg.channel.send(plot)


def setup(bot):
    bot.add_cog(Cmds(bot))
