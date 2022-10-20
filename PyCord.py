# PyCord - A Chat Only Discord Client made in Python
# PyCord is a third-party Discord Client and is not affiliated with Discord.
#
# Python Version: 3.8.10 64-bit
# Github Repository: https://github.com/PyTsun/PyCord

# PACKAGES
# Python Packages that PyCord uses to run properly.
import discord
from discord.ext import commands

from textual.app import App
from rich.panel import Panel
from rich.box import ROUNDED
from textual.widgets import Static
from textual_inputs import TextInput

from httpx import get
from re import search
from notifypy import Notify
from threading import Thread
from dotenv import load_dotenv
from textwrap import TextWrapper
from os import getenv, system, name
from time import strftime, localtime
from asyncio import sleep as aiosleep

# CONFIGURATION
# Configuration that PyCord needs to run and render information properly.
boxType = ROUNDED
currentVersion = "v1.5"
load_dotenv(".env")

serverList = []
channelList = []
serverIndex = 0
channelIndex = 0
serverFocus = ["unknownServer", 0]
channelFocus = ["unknownChannel", 0]
pyCordReady = False

history = "#5865F2"
chatbox = "#8790ed"

# CODE
def clearTerminal():
    system('cls' if name == 'nt' else 'clear')

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

async def replyMessage(id: int, content: str):
    if pyCordReady != True: return
    await bot.get_partial_messageable(channelFocus[1]).get_partial_message(id).reply(content=content)

class PyCord(commands.Bot):
    messageQueue = []
    typingQueue = []
    typingUsers = ""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        intents.typing = True
        super().__init__(command_prefix=[], intents=intents)

    async def updateTyping(self):
        if pyCordReady != True: return

        if len(self.typingQueue) == 0:
            self.typingUsers = f""
        if len(self.typingQueue) == 1:
            self.typingUsers = f"{self.typingQueue[0]} is typing..."
        if len(self.typingQueue) == 2:
            self.typingUsers = f"{self.typingQueue[0]} and {self.typingQueue[1]} is typing..."
        if len(self.typingQueue) >= 2:
            self.typingUsers = f"{self.typingQueue[0]}, {self.typingQueue[1]} and {len(self.typingQueue) - 2} more users is typing..."

        try: await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", subtitle=f"{self.typingUsers}", subtitle_align="left", border_style=history, box=boxType))
        except NameError: pass

    async def on_ready(self):
        global pyCordReady
        for guild in bot.guilds:
            serverList.append(guild.id)
        
        server = bot.get_guild(serverList[0])

        lookforGeneral = True
        for channel in server.channels:
            if isinstance(channel, discord.TextChannel):
                channelList.append(channel.id)

                if lookforGeneral == True:
                    if channel.name.__contains__("general") or channel.name.__contains__("chat"):
                        global channelIndex
                        channelIndex = len(channelList) - 1
                        channelFocus[0] = channel.name
                        channelFocus[1] = channel.id
                        lookforGeneral = False


        serverFocus[0] = server.name
        serverFocus[1] = server.id
        if lookforGeneral == True:
            channel = bot.get_channel(channelList[0])
            channelFocus[0] = channel.name
            channelFocus[1] = channel.id
        print(channelFocus[0])
        r = True
        server = bot.get_guild(server.id)

        async def messageSender():
            while True:
                while self.messageQueue == []:
                    await aiosleep(.1)

                if self.messageQueue[0] != "":
                    try:
                        await bot.get_partial_messageable(channelFocus[1]).send(self.messageQueue[0])
                        self.messageQueue.pop(0)
                    except:
                        serverList.clear()
                        channelList.clear()
                        for guild in bot.guilds:
                            serverList.append(guild.id)

                        server = bot.get_guild(serverList[0])
                        for channel in server.channels:
                            if isinstance(channel, discord.TextChannel):
                                channelList.append(channel.id)

                                if lookforGeneral == True:
                                    if channel.name.__contains__("general") or channel.name.__contains__("chat"):
                                        global channelIndex
                                        channelIndex = len(channelList) - 1
                                        channelFocus[0] = channel.name
                                        channelFocus[1] = channel.id
                                        lookforGeneral = False


                        serverFocus[0] = server.name
                        serverFocus[1] = server.id

                        channel = bot.get_channel(channelList[0])
                        channelFocus[0] = channel.name
                        channelFocus[1] = channel.id
                        PyCordInterface.chatHistory.append("* [red]Error:[/red] Failed to send message to channel.")
                        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style=history, box=boxType))
                else:
                    self.messageQueue.pop(0)
                
        pyCordReady = True
        await bot.loop.create_task(messageSender())

    async def on_guild_join(self, guild: discord.Guild):
        if pyCordReady != True: return
        serverList.clear()
        for guild in bot.guilds:
            serverList.append(guild.id)

        if len(PyCordInterface.chatHistory) >= chats.size.height - 3: PyCordInterface.chatHistory.pop(0)
        PyCordInterface.chatHistory.append(f"* You have been added to [yellow]{guild.name}[/yellow]!")
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style=history, box=boxType))

    async def on_typing(self, channel: discord.TextChannel, user: discord.Member, when):
        if pyCordReady != True: return
        if channel.guild.id != serverFocus[1]: return
        if channel.id != channelFocus[1]: return
        if user.id == bot.user.id: return

        try: self.typingQueue.remove(user.display_name)
        except: pass
        PyCord.typingQueue.append(user.display_name)
        await self.updateTyping()
        await aiosleep(10)
        try: self.typingQueue.remove(user.display_name)
        except: pass
        await self.updateTyping()

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member, reactionEvent = None):
        if pyCordReady != True: return
        if user.guild.id != serverFocus[1]: return
        if reaction.message.channel.id != channelFocus[1]: return
        if reaction.message.author.id != bot.user.id: return

        PyCordInterface.chatHistory.append(f"[cyan]{user.display_name}[/cyan] reacted to your message with {reaction.emoji}")
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style=history, box=boxType))

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if pyCordReady != True: return
        msgAuthor = before.author.display_name
        if before.guild.id != serverFocus[1]: return
        if before.channel.id != channelFocus[1]: return

        if before.author.bot:
            color = ["[blue]", "[/blue]", 23]
        else:
            color = rgb_to_hex(before.author.color.to_rgb())
            color = [f"[{color}]", f"[/{color}]", (len(color) * 4) + 1]

        title = f"{color[0]}{msgAuthor}{color[1]}"
        w = TextWrapper(width=chats.size.width-4, break_long_words=True, replace_whitespace=True)
        messagesb = [w.fill(p) for p in before.content.splitlines()]
        messagesa = [w.fill(p) for p in after.content.splitlines()]
        messagesb = messagesb[0].split("\n")
        messagesa = messagesa[0].split("\n")

        PyCordInterface.chatHistory.append(title + " edited their message.")
        for x in range(len(messagesb)):
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: 
                PyCordInterface.chatHistory.pop(0)
                
            PyCordInterface.chatHistory.append(f"[red]{(messagesb[x])}[/red]")

        for x in range(len(messagesa)):
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: 
                PyCordInterface.chatHistory.pop(0)
                PyCordInterface.chatHistory.pop(0)
                
            PyCordInterface.chatHistory.append(f"{(messagesa[x])}")

        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
        
    async def on_message(self, message: discord.Message):
        if pyCordReady != True: return
        msg = message.content.replace("[", "\[")
        mid = message.id
        msgAuthor = message.author.display_name.encode("ascii", errors="ignore").decode()

        try:
            replyAuthor = message.reference.resolved.author.display_name
            replyContent = message.reference.resolved.content

            if replyContent == "":
                if message.reference.resolved.attachments != []:
                    if message.reference.resolved.attachments != []:
                        if len(message.reference.resolved.attachments) == 1:
                            replyContent += "[dim]Sent 1 attatchment.[/dim] "
                        else:
                            replyContent += f"[dim]Sent {len(message.reference.resolved.attachments)} attatchments.[/dim] "

                    if message.reference.resolved.embeds != []:
                        if len(message.reference.resolved.attachments) == 1:
                            replyContent = "[dim]Sent 1 embed.[/dim]"
                        else:
                            replyContent = f"[dim]Sent {len(message.reference.resolved.embeds)} embeds.[/dim]"
        except: pass
        
        try: self.typingQueue.remove(message.author.display_name)
        except: pass
        await self.updateTyping()

        try: # notify user
            if message.guild.id != serverFocus[1] and message.content.__contains__(f"<@{bot.user.id}>"):
                notif = Notify()
                notif.title = f"{message.author.name} on {message.guild.name} (#{message.channel.name})"
                notif.message = message.content.replace(f"<@{bot.user.id}>", f"@{bot.user.name}")
                notif.send()
        except AttributeError: pass

        if message.guild.id != serverFocus[1]: return
        if message.channel.id != channelFocus[1]: return

        if message.author.bot:
            authorColor = ["[blue]", "[/blue]", 23]
        else:
            authorColor = rgb_to_hex(message.author.color.to_rgb())
            authorColor = [f"[{authorColor}]", f"[/{authorColor}]", int((len(authorColor) * 4) + 1)]

        try:
            if message.reference.resolved.author.bot:
                replyColor = ["[blue]", "[/blue]", 13]
            else:
                replyColor = rgb_to_hex(message.reference.resolved.author.color.to_rgb())
                replyColor = [f"[{replyColor}]", f"[/{replyColor}]", int((len(replyColor) * 4) + 1)]
        except: pass
        
        for word in message.content.split():
            if word.__contains__("#"): # Channel
                try:
                    channelId = search("<#(.*?)>", word).group(1)
                    msg = msg.replace(f"<#{channelId}>", f"[black on #5865F2]#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}[/black on #5865F2]")
                except AttributeError: pass

            if word.__contains__("@&"): # Role
                try:
                    roleId = search("<@&(.*?)>", word).group(1)
                    roleColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(roleId)).color.to_rgb())
                    msg = msg.replace(f"<@&{roleId}>", f"[black on {roleColor}]@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}[/black on {roleColor}]")
                except AttributeError: pass

            if word.__contains__("@!"): # User
                try:
                    userId = search("<@!(.*?)>", word).group(1)
                    userId = userId.replace("&", "")
                    userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                    msg = msg.replace(f"<@!{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                except AttributeError: pass

            if word.__contains__("@"): # User
                try:
                    userId = search("<@(.*?)>", word).group(1)
                    userId = userId.replace("&", "")
                    userId = userId.replace("!", "")
                    userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                    msg = msg.replace(f"<@{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                except AttributeError: pass

            if word.__contains__("***"):
                try:
                    word = search("\*\*\*(.*?)\*\*\*", msg).group(1)
                    msg = msg.replace(f"***{word}***", f"[b][i]{word}[/i][/b]")
                except AttributeError: pass

            if word.__contains__("**"):
                try: 
                    word = search("\*\*(.*?)\*\*", msg).group(1)
                    msg = msg.replace(f"**{word}**", f"[b]{word}[/b]")
                except AttributeError: pass

            if word.__contains__("*"):
                try:
                    word = search("\*(.*?)\*", msg).group(1)
                    msg = msg.replace(f"*{word}*", f"[i]{word}[/i]")
                except AttributeError: pass
            
            if word.__contains__("__"):
                try:
                    word = search("__(.*?)__", msg).group(1)
                    msg = msg.replace(f"__{word}__", f"[u]{word}[/u]")
                except AttributeError: pass
        
        try:
            for word in message.reference.resolved.content.split():
                if word.__contains__("#"): # Channel
                    try:
                        channelId = search("<#(.*?)>", word).group(1)
                        replyContent = replyContent.replace(f"<#{channelId}>", f"[black on #5865F2]#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}[/black on #5865F2]")
                    except AttributeError: pass

                if word.__contains__("@&"): # Role
                    try:
                        roleId = search("<@&(.*?)>", word).group(1)
                        roleColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_role(int(roleId)).color.to_rgb())
                        replyContent = replyContent.replace(f"<@&{roleId}>", f"[black on {roleColor}]@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}[/black on {roleColor}]")
                    except AttributeError: pass

                if word.__contains__("@!"): # User
                    try:
                        userId = search("<@!(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                        replyContent = replyContent.replace(f"<@!{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                    except AttributeError: pass

                if word.__contains__("@"): # User
                    try:
                        userId = search("<@(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userId = userId.replace("!", "")
                        userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                        replyContent = replyContent.replace(f"<@{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                    except AttributeError: pass

                if word.__contains__("***"):
                    try:
                        word = search("\*\*\*(.*?)\*\*\*", replyContent).group(1)
                        replyContent = replyContent.replace(f"***{word}***", f"[b][i]{word}[/i][/b]")
                    except AttributeError: pass

                if word.__contains__("**"):
                    try: 
                        word = search("\*\*(.*?)\*\*", replyContent).group(1)
                        replyContent = replyContent.replace(f"**{word}**", f"[b]{word}[/b]")
                    except AttributeError: pass

                if word.__contains__("*"):
                    try:
                        word = search("\*(.*?)\*", replyContent).group(1)
                        replyContent = replyContent.replace(f"*{word}*", f"[i]{word}[/i]")
                    except AttributeError: pass
                
                if word.__contains__("__"):
                    try:
                        word = search("__(.*?)__", replyContent).group(1)
                        replyContent = replyContent.replace(f"__{word}__", f"[u]{word}[/u]")
                    except AttributeError: pass
        except: pass

        dateTime = strftime("%m/%d/%y %I:%M%p", localtime(message.created_at.timestamp()))
        title = f"{authorColor[0]}{msgAuthor}{authorColor[1]}\t[dim]{dateTime}[/dim] {mid}".expandtabs((chats.size.width + authorColor[2] - 15) - (len(str(mid)) + len(str(dateTime))))
        w = TextWrapper(width=chats.size.width-4, break_long_words=True, replace_whitespace=True)
        if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
        
        try:
            PyCordInterface.chatHistory.append(f"╭── {replyColor[0]}{replyAuthor}{replyColor[1]}: {(replyContent[:57 ] + '...') if len(replyContent) > 57  else replyContent}")
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
        except: pass

        if message.content != "":
            messages = [w.fill(p) for p in msg.splitlines()]
            if "\n" in messages[0]:
                messages = messages[0].split("\n")
    
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: 
                PyCordInterface.chatHistory.pop(0)
                PyCordInterface.chatHistory.pop(0)

            PyCordInterface.chatHistory.append(title)
            for x in range(len(messages)):
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
                PyCordInterface.chatHistory.append(f"{(messages[x])}")

            if message.attachments != []:
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                if len(message.attachments) == 1:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 attatchment.[/dim]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.attachments)} attatchments.[/dim]")

            await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))

        else:
            PyCordInterface.chatHistory.append(title)
            if message.attachments != []:
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                if len(message.attachments) == 1:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 attatchment.[/dim]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.attachments)} attatchments.[/dim]")

            if message.embeds != []:
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                if len(message.embeds) == 1:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 embed.[/dim]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.embeds)} embeds.[/dim]")

            await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
        chats.refresh

bot = PyCord()
    
class PyCordInterface(App):
    chatHistory = []
    
    async def on_load(self) -> None:
        global pyCordReady
        token = getenv("token")
        try: Thread(target=bot.run, kwargs={"token": token}).start()
        except KeyboardInterrupt: pass

        await self.bind("q", "quit", "Quit")
        await self.bind("enter", "submit", "Send Message")
        await self.bind("Z", "previousChannel", "Previous Channel")
        await self.bind("X", "nextChannel", "Next Channel")
        await self.bind("z", "previousServer", "Previous Server")
        await self.bind("x", "nextServer", "Next Server")
        await self.bind("r", "refresh", "Clear Messages")
        await self.bind("a", "toggleTopic", "Toggle Channel Topic")
        
        clearTerminal()
        print("* Checking for PyCord Updates...")
        api = get("https://api.github.com/repos/PyTsun/PyCord/releases/latest").json()
        if api["tag_name"] != currentVersion:
            tag = api["tag_name"]
            title = api["name"]
            info = api["body"]
            print( "* PyCord Update Available!\n")
            print(f"[{tag}] {title}\n{info}")
            print( "\n* Visit https://github.com/PyTsun/PyCord/releases to download update!")
        
            await aiosleep(5)
        else:
            print("* No Updates Available.")
        
        while pyCordReady == False:
            await aiosleep(.1)

        print("* Checking Server List...")
        if len(bot.guilds) == 0:
            print("* Your Discord Bot is Currently on 0 Guilds. Please invite your bot to a Discord Server to continue!")
            while bot.guilds.count == 0:
                await aiosleep(1)
        print(f"* Currently on {str(len(bot.guilds))} servers")
    
        await aiosleep(1.5)
        
    async def action_quit(self) -> None:

        return await super().action_quit()
    
    async def displayHistory(self):
        await chats.update(Panel("", title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", subtitle="Loading...", subtitle_align="left", border_style=history, box=boxType))
        lastChannel = channelFocus[1]
        await aiosleep(1)
        if lastChannel != channelFocus[1]: return
        await chats.update(Panel("", title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style=history, box=boxType))
        channel = bot.get_channel(channelFocus[1])

        messages = [message async for message in channel.history(limit=24)]
        messages.reverse()

        for message in messages:
            msg = message.content.replace("[", "\[")
            mid = message.id
            msgAuthor = message.author.display_name.encode("ascii", errors="ignore").decode()
            
            replyAuthor = None
            replyContent = None

            try:
                replyAuthor = message.reference.resolved.author.display_name
                replyContent = message.reference.resolved.content

                if replyContent == "":
                    if message.reference.resolved.attachments != []:
                        if message.reference.resolved.attachments != []:
                            if len(message.reference.resolved.attachments) == 1:
                                replyContent += "[dim]Sent 1 attatchment.[/dim] "
                            else:
                                replyContent += f"[dim]Sent {len(message.reference.resolved.attachments)} attatchments.[/dim] "

                        if message.reference.resolved.embeds != []:
                            if len(message.reference.resolved.attachments) == 1:
                                replyContent = "[dim]Sent 1 embed.[/dim]"
                            else:
                                replyContent = f"[dim]Sent {len(message.reference.resolved.embeds)} embeds.[/dim]"
            except: pass

            try: PyCord.typingQueue.remove(message.author.display_name)
            except: pass

            if message.guild.id != serverFocus[1]: return
            if message.channel.id != channelFocus[1]: return

            if message.author.bot:
                authorColor = ["[blue]", "[/blue]", 23]
            else:
                authorColor = rgb_to_hex(message.author.color.to_rgb())
                authorColor = [f"[{authorColor}]", f"[/{authorColor}]", int((len(authorColor) * 4) + 1)]

            try:
                if message.reference.resolved.author.bot:
                    replyColor = ["[blue]", "[/blue]", 13]
                else:
                    replyColor = rgb_to_hex(message.reference.resolved.author.color.to_rgb())
                    replyColor = [f"[{replyColor}]", f"[/{replyColor}]", int((len(replyColor) * 4) + 1)]
            except: pass

            for word in message.content.split():
                if word.__contains__("#"): # Channel
                    try:
                        channelId = search("<#(.*?)>", word).group(1)
                        msg = msg.replace(f"<#{channelId}>", f"[black on #5865F2]#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}[/black on #5865F2]")
                    except AttributeError: pass

                if word.__contains__("@&"): # Role
                    try:
                        roleId = search("<@&(.*?)>", word).group(1)
                        roleColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_role(int(roleId)).color.to_rgb())
                        msg = msg.replace(f"<@&{roleId}>", f"[black on {roleColor}]@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}[/black on {roleColor}]")
                    except AttributeError: pass

                if word.__contains__("@!"): # User
                    try:
                        userId = search("<@!(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                        msg = msg.replace(f"<@!{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                    except AttributeError: pass

                if word.__contains__("@"): # User
                    try:
                        userId = search("<@(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userId = userId.replace("!", "")
                        userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                        msg = msg.replace(f"<@{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                    except AttributeError: pass

                if word.__contains__("***"):
                    try:
                        word = search("\*\*\*(.*?)\*\*\*", msg).group(1)
                        msg = msg.replace(f"***{word}***", f"[b][i]{word}[/i][/b]")
                    except AttributeError: pass

                if word.__contains__("**"):
                    try: 
                        word = search("\*\*(.*?)\*\*", msg).group(1)
                        msg = msg.replace(f"**{word}**", f"[b]{word}[/b]")
                    except AttributeError: pass

                if word.__contains__("*"):
                    try:
                        word = search("\*(.*?)\*", msg).group(1)
                        msg = msg.replace(f"*{word}*", f"[i]{word}[/i]")
                    except AttributeError: pass
                
                if word.__contains__("__"):
                    try:
                        word = search("__(.*?)__", msg).group(1)
                        msg = msg.replace(f"__{word}__", f"[u]{word}[/u]")
                    except AttributeError: pass
            
            try:
                for word in message.reference.resolved.content.split():
                    if word.__contains__("#"): # Channel
                        try:
                            channelId = search("<#(.*?)>", word).group(1)
                            replyContent = replyContent.replace(f"<#{channelId}>", f"[black on #5865F2]#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}[/black on #5865F2]")
                        except AttributeError: pass

                    if word.__contains__("@&"): # Role
                        try:
                            roleId = search("<@&(.*?)>", word).group(1)
                            roleColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_role(int(roleId)).color.to_rgb())
                            replyContent = replyContent.replace(f"<@&{roleId}>", f"[black on {roleColor}]@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}[/black on {roleColor}]")
                        except AttributeError: pass

                    if word.__contains__("@!"): # User
                        try:
                            userId = search("<@!(.*?)>", word).group(1)
                            userId = userId.replace("&", "")
                            userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                            replyContent = replyContent.replace(f"<@!{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                        except AttributeError: pass

                    if word.__contains__("@"): # User
                        try:
                            userId = search("<@(.*?)>", word).group(1)
                            userId = userId.replace("&", "")
                            userId = userId.replace("!", "")
                            userColor = rgb_to_hex(bot.get_guild(serverFocus[1]).get_member(int(userId)).color.to_rgb())
                            replyContent = replyContent.replace(f"<@{userId}>", f"[black on {userColor}]@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}[/black on {userColor}]")
                        except AttributeError: pass

                    if word.__contains__("***"):
                        try:
                            word = search("\*\*\*(.*?)\*\*\*", replyContent).group(1)
                            replyContent = replyContent.replace(f"***{word}***", f"[b][i]{word}[/i][/b]")
                        except AttributeError: pass

                    if word.__contains__("**"):
                        try: 
                            word = search("\*\*(.*?)\*\*", replyContent).group(1)
                            replyContent = replyContent.replace(f"**{word}**", f"[b]{word}[/b]")
                        except AttributeError: pass

                    if word.__contains__("*"):
                        try:
                            word = search("\*(.*?)\*", replyContent).group(1)
                            replyContent = replyContent.replace(f"*{word}*", f"[i]{word}[/i]")
                        except AttributeError: pass
                    
                    if word.__contains__("__"):
                        try:
                            word = search("__(.*?)__", replyContent).group(1)
                            replyContent = replyContent.replace(f"__{word}__", f"[u]{word}[/u]")
                        except AttributeError: pass
            except: pass

            dateTime = strftime("%m/%d/%y %I:%M%p", localtime(message.created_at.timestamp()))
            title = f"{authorColor[0]}{msgAuthor}{authorColor[1]}\t[dim]{dateTime}[/dim] {mid}".expandtabs((chats.size.width + authorColor[2] - 15) - (len(str(mid)) + len(str(dateTime))))
            w = TextWrapper(width=chats.size.width-12, break_long_words=True, replace_whitespace=True)
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

            try:
                PyCordInterface.chatHistory.append(f"╭── {replyColor[0]}{replyAuthor}{replyColor[1]}: {(replyContent[:57 ] + '...') if len(replyContent) > 57  else replyContent}")
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
            except: pass

            if message.content != "":
                messages = [w.fill(p) for p in msg.splitlines()]
                if "\n" in messages[0]:
                    messages = messages[0].split("\n")

                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: 
                    PyCordInterface.chatHistory.pop(0)
                    PyCordInterface.chatHistory.pop(0)

                PyCordInterface.chatHistory.append(title)
                for x in range(len(messages)):
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
                    PyCordInterface.chatHistory.append(f"{(messages[x])}")

                if message.attachments != []:
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                    if len(message.attachments) == 1:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 attatchment.[/dim]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.attachments)} attatchments.[/dim]")

                await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style=history, box=boxType))

            else:
                PyCordInterface.chatHistory.append(title)
                if message.attachments != []:
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                    if len(message.attachments) == 1:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 attatchment.[/dim]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.attachments)} attatchments.[/dim]")

                if message.embeds != []:
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                    if len(message.embeds) == 1:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent 1 embed.[/dim]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [dim]Sent {len(message.embeds)} embeds.[/dim]")

                await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style=history, box=boxType))
        chats.refresh
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))

    async def action_previousServer(self):
        global serverIndex
        
        if serverIndex - 1 == -1: return
        if not serverIndex - 1 == -1:
            serverIndex -= 1

            try:
                guildFocus = bot.get_guild(serverList[serverIndex])
                serverFocus[0] = guildFocus.name
                serverFocus[1] = guildFocus.id

                server = bot.get_guild(serverList[serverIndex])
    
                channelList.clear()
                lookforGeneral = True
                for channel in server.channels:
                    if isinstance(channel, discord.TextChannel):
                        channelList.append(channel.id)

                        if lookforGeneral == True:
                            if channel.name.__contains__("general") or channel.name.__contains__("chat"):
                                global channelIndex
                                channelIndex = len(channelList) - 1
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False
                                
                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        if len(self.chatHistory) >= chats.size.height - 2: self.chatHistory.pop(0)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))

    async def action_nextServer(self):
        global serverIndex
        
        if serverIndex >= len(serverList) - 1: return
        if not serverIndex >= len(serverList) - 1:
            serverIndex += 1

            try:
                guildFocus = bot.get_guild(serverList[serverIndex])
                serverFocus[0] = guildFocus.name
                serverFocus[1] = guildFocus.id
                server = bot.get_guild(serverList[serverIndex])

                channelList.clear()
                lookforGeneral = True
                for channel in server.channels:
                    if isinstance(channel, discord.TextChannel):
                        channelList.append(channel.id)

                        if lookforGeneral == True:
                            if channel.name.__contains__("general") or channel.name.__contains__("chat"):
                                global channelIndex
                                channelIndex = len(channelList) - 1
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False

                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        if len(self.chatHistory) >= chats.size.height - 2: self.chatHistory.pop(0)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))

    async def action_previousChannel(self):
        global channelIndex

        if channelIndex - 1 == - 1: return
        if not channelIndex - 1 == - 1:
            channelIndex -= 1
            
            try:
                guildFocus = bot.get_channel(channelList[channelIndex])
                channelFocus[0] = guildFocus.name
                channelFocus[1] = guildFocus.id
            except: pass
        
        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        if len(self.chatHistory) >= chats.size.height - 2: self.chatHistory.pop(0)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
        
    async def action_nextChannel(self):
        global channelIndex

        if channelIndex >= len(channelList) - 1: return
        if not channelIndex >= len(channelList) - 1:
            channelIndex += 1

            try:
                guildFocus = bot.get_channel(channelList[channelIndex])
                channelFocus[0] = guildFocus.name
                channelFocus[1] = guildFocus.id
            except: pass
        
        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        if len(self.chatHistory) >= chats.size.height - 2: self.chatHistory.pop(0)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))

    async def action_refresh(self):
        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
    
    async def action_submit(self):
        if chatBox.value.startswith("/reply"):
            args = chatBox.value.split()
            id = int(args[1])
            args.pop(0)
            args.pop(0)
            content = " ".join(args)
            chatBox._cursor_position = 0
            chatBox.value = ""
            return replyMessage(id, content)

        if chatBox.value.startswith("/leave"):
            try:
                guildFocus = bot.get_guild(serverList[serverIndex])
                serverFocus[0] = guildFocus.name
                serverFocus[1] = guildFocus.id
                server = bot.get_guild(serverList[serverIndex])

                channelList.clear()
                lookforGeneral = True
                for channel in server.channels:
                    if isinstance(channel, discord.TextChannel):
                        channelList.append(channel.id)

                        if lookforGeneral == True:
                            if channel.name.__contains__("general") or channel.name.__contains__("chat"):
                                global channelIndex
                                channelIndex = len(channelList) - 1
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False

                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

            chatBox._cursor_position = 0
            chatBox.value = ""
            return bot.loop.create_task(bot.get_guild(serverFocus[1]).leave())
        
        PyCord.messageQueue.append(chatBox.value)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
        chatBox._cursor_position = 0
        chatBox.value = ""

    async def on_mount(self):
        global chatBox
        global chats

        chatBox = TextInput()
        chatBox.border_style = chatbox
        chats = Static(renderable=Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style=history, box=boxType))
        
        self.set_interval(.15, chats.refresh)
        await self.view.dock(chatBox, edge="bottom", size=3)
        await self.view.dock(chats, edge="top", size=500)

        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", title_align="left", border_style=history, box=boxType))
        bot.loop.create_task(self.displayHistory())
        self.chatHistory.clear()


PyCordInterface.run()
