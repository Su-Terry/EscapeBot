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

# async def hintInCmds(ctx):
#     user = ctx.author.name
#     with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
#         jdata = json.load(jfile)
#     return 'hint' in jdata['cmds']

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
    return 'inspect' in jdata['cmds']

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
            description="Objs in room: {}".format(', '.join(jdata[f"{jdata['room_at']}_object"])),
            color=0xedf10e)
        embed.set_author(name="Made by: oceansfavor", 
            url="https://www.instagram.com/oceansfavor/", 
            icon_url="https://i.imgur.com/tax7zpT.jpg")
        for place in jdata['rooms']:
            if place == jdata['room_at']: continue
            objects = jdata[f'{place}_object']
            embed.add_field(name=place, value="Stuff: {}".format(', '.join(objects)), inline=True)
        embed.set_footer(text=f"{user} is playing!")

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
            return f'Welcome to ESCAPE, {player}'
        elif result == 'ESCAPE':
            return f"{player} escaped successfully!"
        elif result == 'QUIT':
            return "Thanks for playing!"
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
                await msg.channel.send('Quit entering password mode')
            if txt == jdata[f'{inInputPasswd}_passwd']:
                jdata[f'{inInputPasswd}_status'] = 'open'
                plots = self.getCmdPlot(f'{inInputPasswd}_open_plot', user)
                for plot in plots:
                    if plot == 'next!':
                        self.nextRoom(user)
                        plots = self.getRoomPlot(user)
                        for plot in plots:
                            if plot == 'escaped!':
                                await msg.channel.send(embed=self.getTxtEmbed('ESCAPE', user))
                                return
                            else:
                                await msg.channel.send(plot)
                            await msg.channel.send(embed=self.getRoomEmbed(user))
                    else:
                        await msg.channel.send(plot)
                inInputPasswd = jdata['inInputPasswd'] = ''
            else:
                await msg.channel.send('Incorrect password')

        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            json.dump(jdata, jfile, indent=4)

    @commands.group(brief='call escape game')
    async def escape(self, msg) -> None:
        await msg.channel.send('Enter "escape H" to check the rules.')

    @escape.command(brief='new game, "escape N"')
    async def N(self, msg) -> None:
        user = msg.author.name
        self.newGame(user)
        await msg.channel.send(embed=self.getTxtEmbed('NEW', user))
        plots = self.getRoomPlot(user)
        for plot in plots:
            await msg.channel.send(plot)
        await msg.channel.send(embed=self.getRoomEmbed(user))

    @escape.command(brief='load game, "escape L"')
    async def L(self, msg) -> None:
        user = msg.author.name
        
        if not os.path.isfile(f'User/users/{user}.json'):
            await msg.channel.send('No game record.')
            return
        self.loadGame(user)
        await msg.channel.send(embed=self.getTxtEmbed('LOAD', user))
        plots = self.getRoomPlot(user)
        for plot in plots:
            await msg.channel.send(plot)
        await msg.channel.send(embed=self.getRoomEmbed(user))

    @escape.command(brief='Game rules, "escape H"')
    async def H(self, msg) -> None:
        await msg.channel.send('Enter "escape N" to start new game.')
        await msg.channel.send('Enter "escape L" to load game.')
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        for cmd in jdata['cmds']:
            await msg.channel.send(jdata[cmd])
        if len(jdata['cmds']) == 0:
            await msg.channel.send('Currently no game cmd.')
        else:
            await msg.channel.send('Usage: "{verb} {noun}"')

    # @commands.check(inGame)
    # @commands.check(hintInCmds)
    # @commands.command(brief='See the hint, "HINT"')
    # async def hint(self, msg) -> None:
    #     user = msg.author.name
    #     with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
    #         jdata = json.load(jfile)
    #     await msg.channel.send(jdata['hint'][int(jdata['room_plot_idx'])])
    #     await msg.channel.send("There's no hint in this level.")

    @commands.check(inGame)
    @commands.check(mvInCmds)
    @commands.command(brief='Move [object] to [place], "mv [object] [place]"')
    async def mv(self, msg, object:str, place:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if 'mv' not in jdata['cmds']: return
        if object not in jdata['objects']:
            await msg.channel.send('Object: Not existing or unable to move.')
            return
        if place not in jdata['positions'] + jdata['rooms']:
            await msg.channel.send('Place: Not a legal position for moving to.')
            return
        if object not in jdata[f'{jdata["room_at"]}_object']:
            await msg.channel.send('Object: The Object is not in the current room.')
            return
        if object in jdata[f'{jdata[place]}_object']:
            await msg.channel.send(f'Moving: The [{object}] has already in [{place}].')
            return
        jdata[f'{place}_object'].append(object)
        for i in jdata['positions']+jdata['rooms']:
            if object in jdata[i]:
                jdata[i].remove(object)
                await msg.channel.send(f'Moved [{object}] from [{i}] to [{place}].')
        plots = self.getCmdPlot(f'mv {object} {place}_plot', user)
        for plot in plots:
            await msg.channel.send(plot)
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

    @commands.check(inGame)
    @commands.check(gotoInCmds)
    @commands.command(brief='Go to [place], "goto {place}"')
    async def goto(self, msg, place:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if 'goto' not in jdata['cmds']: return
        if place == jdata['at']:
            await msg.channel.send('Failed: You are already here.')
        if place in jdata['positions']:
            jdata['at'] = place
            await msg.channel.send(f'Went to [{place}].')
            plots = self.getCmdPlot(f'goto {place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
        elif place in jdata['rooms']:
            jdata['at'] = jdata['room_at'] = place
            await msg.channel.send(f'Went to [{place}].')
            plots = self.getCmdPlot(f'{place}_plot', user)
            for plot in plots:
                await msg.channel.send(plot)
            await msg.channel.send(embed=self.getRoomEmbed(user))
        else:
            await msg.channel.send('Place: Not existing or unable for goin to.')
        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

    @commands.check(inGame)
    @commands.check(checkInCmds)
    @commands.command(brief='See the plot of bracketed text, "inspect [room/place/obj]/(attachment)"')
    async def inspect(self, msg, name:str) -> None:
        user = msg.author.name
        with open(f'User/users/{user}.json', 'r', encoding='utf8') as jfile:
            jdata = json.load(jfile)
        if 'inspect' not in jdata['cmds']: return
        jdata['inInputPasswd'] = ''
        
        attachment_name = f'{jdata["inCheck"]}_{name}'
        if attachment_name in jdata['attachments']:
            jdata["inCheck"] = attachment_name
            if attachment_name in jdata["lock"]:
                lock_status = jdata[f'{attachment_name}_status']
                plots = jdata[f'{attachment_name}_{lock_status}_plot']
                if lock_status == 'lock':
                    jdata['inInputPasswd'] = attachment_name
                    await msg.channel.send("Enter x to exit the typing mode.")
            else:
                plots = jdata[f'{attachment_name}_plot']
        elif name in jdata['rooms']+jdata['positions']+jdata['objects']:
            # if name in jdata['positions']:
            #     exect_name = f"{jdata['room_at']}_position"
            # pass
            jdata['inCheck'] = name
            plots = jdata[f'{name}_plot']
        else:
            await msg.channel.send('The thing is not exist at your position.')
            return

        with open(f'User/users/{user}.json', 'w', encoding='utf8') as jfile:
            jdata = json.dump(jdata, jfile, indent=4)

        self.addItem(plots, user)
        for plot in plots:
            await msg.channel.send(plot)


async def setup(bot):
    await bot.add_cog(Escape(bot))
