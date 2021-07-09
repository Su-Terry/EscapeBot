# encoding: utf-8
import discord
from core.classes import Cog_Extension
from discord.ext import commands
import os, json


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


def setup(bot):
    bot.add_cog(Escape(bot))
