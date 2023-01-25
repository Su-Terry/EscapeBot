# encoding: utf-8
import discord
from core.classes import Cog_Extension
from discord.ext import commands
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

class Escape(Cog_Extension):

    def __init__(self, bot):
        super().__init__(bot)

    def newGame(self, user:str):
        with open(f'User/userlist.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            if user not in jdata['users']:
                jdata['users'].append(user)
        with open(f'User/userlist.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

        with open(f'level/1.json', 'r', encoding='utf8') as jInputFile:
            txt = jInputFile.readlines()
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jOutPutFile:
            jOutPutFile.writelines(txt)

        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            jdata['inGame'] = "TRUE"
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    def loadGame(self, user:str):
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            jdata['inGame'] = "TRUE"
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    def nextRoom(self, user:str):
        """Simply add `room_plot_idx` by one"""
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            jdata['room_plot_idx'] = str(int(jdata['room_plot_idx']) + 1)
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    def addItem(self, plots:list, user:str):
        """From `plots` to add items such as `rooms`, `positions`, 
        `objects`, and `attachments`.
        Besides that, we add `cmds` in the meanwhile.
        """
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        for plot in plots:
            for position in jdata['position_all']:
                if position in plot and position not in jdata['positions']:
                    jdata['positions'].append(position)
                    jdata[f'{jdata["room_at"]}_position'].append(position)
            for object in jdata['object_all']:
                if object in plot and object not in jdata['objects']:
                    jdata['objects'].append(object)
                    jdata[f'{jdata["room_at"]}_object'].append(object)
                    if f'{jdata["inCheck"]}_object' in jdata:
                        jdata[f'{jdata["inCheck"]}_object'].append(object)
            attachment:str
            for attachment in jdata['attachment_all']:
                owner_name, name = map(str, attachment.split('_'))
                if owner_name == jdata['inCheck'] and name in plot and attachment not in jdata['attachments']:
                    jdata['attachments'].append(attachment)
            for cmd in jdata['cmd_all']:
                if cmd in plot and cmd not in jdata['cmds']:
                    jdata['cmds'].append(cmd)
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    def getRoomPlot(self, user:str):
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        for room in jdata['room_order'][int(jdata['room_plot_idx'])]:
            jdata['rooms'].append(room)
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)
        plots:list
        plots = jdata['room_plot'][int(jdata['room_plot_idx'])]
        self.addItem(plots, user)
        return plots

    def getCmdPlot(self, _plot:str, user:str):
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        plots:list
        plots = jdata[_plot] if _plot in jdata else []
        return plots

    def getRoomEmbed(self, user:str):
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        embed = discord.Embed(title=jdata['room_at'],
            description="這個房間裡有: {}".format(', '.join(jdata[f"{jdata['room_at']}_object"])),
            color=0xedf10e)
        embed.set_author(name="Made by: oceansfavor", 
            url="https://www.instagram.com/oceansfavor/", 
            icon_url="https://i.imgur.com/tax7zpT.jpg")
        for place in jdata['rooms']:
            if place == jdata['room_at']: continue
            objects = jdata[f'{place}_object']
            embed.add_field(name=place, value="東西: {}".format(', '.join(objects)), inline=True)
        embed.set_footer(text=f"{user}正在玩!")

        return embed

    def getTxtEmbed(self, result:str, user:str):
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            if result in ['ESCAPE', 'QUIT']:
                jdata['inGame'] = "FALSE"
                with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
                    json.dump(jdata, jfile, indent=4)
        embed = discord.Embed(title="escape",
            description=self.getText(result, user),
            color=0xedf10e)
        embed.set_author(name="Made by: oceansfavor", 
            url="https://www.instagram.com/oceansfavor/", 
            icon_url="https://i.imgur.com/tax7zpT.jpg")
        return embed

    def getText(self, result:str, player=''):
        if result == 'NEW' or result == 'LOAD':
            return f'歡迎遊玩escape, {player}'
        elif result == 'ESCAPE':
            return f"{player}逃脫成功!"
        elif result == 'QUIT':
            return "感謝你的遊玩"
        else:
            raise "result not found"

    @commands.Cog.listener()
    async def on_message(self, msg) -> None:
        if msg.author == self.bot.user: return

        user = msg.author.name
        if not os.path.isfile(f'User/users/{user}.json'): return

        with open('User/userlist.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
            if user not in jdata['users']: return

        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if jdata['inGame'] == "FALSE": return

        txt = msg.content.lower()
        if txt == 'q' or txt == 'quit':
            await msg.channel.send(embed=self.getTxtEmbed("QUIT", user))
            return

        inInputPasswd = jdata['inInputPasswd']
        if inInputPasswd != '':
            if txt in jdata['cmds']: return
            if txt == 'x':
                inInputPasswd = jdata['inInputPasswd'] = ''
                await msg.channel.send('已離開輸入密碼的模式')
            if txt == jdata[f'{inInputPasswd}_passwd']:
                jdata[f'{inInputPasswd}_status'] = 'open'
                plots = self.getCmdPlot(f'{inInputPasswd}_open_plot', user)
                for plot in plots:
                    if plot == 'next!':
                        self.nextRoom(user)
                        plots = self.getRoomPlot(user)
                        for plot in plots:
                            if plot == 'escape!':
                                await msg.channel.send(embed=self.getTxtEmbed('ESCAPE', user))
                                return
                            else:
                                await msg.channel.send(plot)
                            await msg.channel.send(embed=self.getRoomEmbed(user))
                    else:
                        await msg.channel.send(plot)
                inInputPasswd = jdata['inInputPasswd'] = ''
            else:
                await msg.channel.send('密碼錯誤')

        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    @commands.group(brief='call escape game')
    async def escape(self, msg) -> None:
        await msg.channel.send('輸入"escape H"查看規則')

    @escape.command(brief='新遊戲, "escape N"')
    async def N(self, msg) -> None:
        user = msg.author.name
        self.newGame(user)
        await msg.channel.send(embed=self.getTxtEmbed('NEW', user))
        plots = self.getRoomPlot(user)
        for plot in plots:
            await msg.channel.send(plot)
        await msg.channel.send(embed=self.getRoomEmbed(user))

    @escape.command(brief='載入遊戲, "escape L"')
    async def L(self, msg) -> None:
        user = msg.author.name
        
        if not os.path.isfile(f'User/users{user}.json'):
            await msg.channel.send('沒有找到你的遊戲紀錄')
            return
        self.loadGame(user)
        await msg.channel.send(embed=self.getTxtEmbed('LOAD', user))
        plots = self.getRoomPlot(user)
        for plot in plots:
            await msg.channel.send(plot)
        await msg.channel.send(embed=self.getRoomEmbed(user))

    @escape.command(brief='查詢指令規則, "escape H"')
    async def H(self, msg) -> None:
        await msg.channel.send('輸入"escape N" 開啟新遊戲')
        await msg.channel.send('輸入"escape L" 載入舊遊戲')
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        for cmd in jdata['cmds']:
            await msg.channel.send(jdata[cmd])
        if len(jdata['cmds']) == 0:
            await msg.channel.send('目前沒有命令可供使用')
        else:
            await msg.channel.send('注意: 以上都不用輸入括號')

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
        plots = self.getCmdPlot(f'mv {object} {place}_plot', user)
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
            plots = self.getCmdPlot(f'goto {place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
        elif place in jdata['rooms']:
            jdata['at'] = jdata['room_at'] = place
            await msg.channel.send(f'已移動至[{place}]!')
            plots = self.getCmdPlot(f'{place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
            await msg.channel.send(embed=self.getRoomEmbed(user))
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

        self.addItem(plots, user)
        for plot in plots:
            await msg.channel.send(plot)


async def setup(bot):
    await bot.add_cog(Escape(bot))
