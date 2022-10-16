# PyCord - A Chat Only Discord Client made in Python
# PyCord is a third-party Discord Client and is not affiliated with Discord.
#
#
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
from textual.reactive import Reactive
from asyncio import sleep as aiosleep
from time import sleep, strftime, localtime

# CONFIGURATION
# Configuration that PyCord need to run and render things properly.
boxType = ROUNDED
load_dotenv(".env")

serverList = []
channelList = []
serverIndex = 0
channelIndex = 0
serverFocus = ["unknownServer", 0]
channelFocus = ["unknownChannel", 0]
pyCordReady = False

# CODE
def clearTerminal():
    system('cls' if name == 'nt' else 'clear')

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

        try: await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", subtitle=f"{self.typingUsers}", subtitle_align="left", border_style="cyan", box=boxType))
        except NameError: pass

    async def on_ready(self):
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
                        serverFocus[0] = server.name
                        serverFocus[1] = server.id
                        channel = bot.get_channel(channelList[0])
                        channelFocus[0] = channel.name
                        channelFocus[1] = channel.id
                        PyCordInterface.chatHistory.append("* [red]Error:[/red] Failed to send message to channel.")
                        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=boxType))
                else:
                    self.messageQueue.pop(0)
                
        
        await bot.loop.create_task(messageSender())

    async def on_guild_join(self, guild: discord.Guild):
        if pyCordReady != True: return
        serverList.clear()
        for guild in bot.guilds:
            serverList.append(guild.id)

        if len(PyCordInterface.chatHistory) >= chats.size.height - 3: PyCordInterface.chatHistory.pop(0)
        PyCordInterface.chatHistory.append(f"* You have been added to [yellow]{guild.name}[/yellow]!")
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=boxType))

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
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=boxType))

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if pyCordReady != True: return
        msgAuthor = before.author.display_name
        if before.guild.id != serverFocus[1]: return
        if before.channel.id != channelFocus[1]: return

        if before.author.bot:
            color = ["[blue]", "[/blue]", 13]
        else:
            color = ["[cyan]", "[/cyan]", 13]
        
        if before.author.id == bot.user.id:
            color = ["[green]", "[/green]", 15]

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

        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
        
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
                            replyContent += "╰── [cyan]Sent 1 attatchment.[/cyan] "
                        else:
                            replyContent += f"╰── [cyan]Sent {len(message.reference.resolved.attachments)} attatchments.[/cyan] "

                    if message.reference.resolved.embeds != []:
                        if len(message.reference.resolved.attachments) == 1:
                            replyContent = "╰── [cyan]Sent 1 embed.[/cyan]"
                        else:
                            replyContent = f"╰── [cyan]Sent {len(message.reference.resolved.embeds)} embeds.[/cyan]"
        except: pass
        
        try: self.typingQueue.remove(message.author.display_name)
        except: pass
        await self.updateTyping()

        try:
            if message.guild.id != serverFocus[1] and message.content.__contains__(f"<@{bot.user.id}>"):
                notif = Notify()
                notif.title = f"{message.author.name} on {message.guild.name} (#{message.channel.name})"
                notif.message = message.content.replace(f"<@{bot.user.id}>", f"@{bot.user.name}")
                notif.send()
        except AttributeError: pass

        if message.guild.id != serverFocus[1]: return
        if message.channel.id != channelFocus[1]: return

        if message.author.bot:
            color = ["[blue]", "[/blue]", 23]
        else:
            color = ["[cyan]", "[/cyan]", 23]
        
        if message.author.id == bot.user.id:
            color = ["[green]", "[/green]", 25]

        if message.author.id == message.guild.owner.id:
            color = ["[yellow]", "[/yellow]", 27]

        try:
            if message.reference.resolved.author.bot:
                rColor = ["[blue]", "[/blue]", 13]
            else:
                rColor = ["[cyan]", "[/cyan]", 13]

            if message.reference.resolved.author.id == bot.user.id:
                rColor = ["[green]", "[/green]", 15]

            if message.reference.resolved.author.id == message.guild.owner.id:
                rColor = ["[yellow]", "[/yellow]", 17]
        except: pass

        for word in message.content.split():
            if word.__contains__("#"): # Channel
                try:
                    channelId = search("<#(.*?)>", word).group(1)
                    msg = msg.replace(f"<#{channelId}>", f"#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}")
                except AttributeError: pass
            if word.__contains__("@&"): # Role
                try:
                    roleId = search("<@&(.*?)>", word).group(1)
                    msg = msg.replace(f"<@&{roleId}>", f"@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}")
                except AttributeError: pass
            if word.__contains__("@!"): # User
                try:
                    userId = search("<@!(.*?)>", word).group(1)
                    userId = userId.replace("&", "")
                    msg = msg.replace(f"<@!{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                except AttributeError: pass
            if word.__contains__("@"): # User
                try:
                    userId = search("<@(.*?)>", word).group(1)
                    userId = userId.replace("&", "")
                    userId = userId.replace("!", "")
                    msg = msg.replace(f"<@{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                except AttributeError: pass
            
        
        try:
            for word in message.reference.resolved.content.split():
                if word.__contains__("#"): # Channel
                    try:
                        channelId = search("<#(.*?)>", word).group(1)
                        replyContent = replyContent.replace(f"<#{channelId}>", f"#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}")
                    except AttributeError: pass
                if word.__contains__("@&"): # Role
                    try:
                        roleId = search("<@&(.*?)>", word).group(1)
                        replyContent = replyContent.replace(f"<@&{roleId}>", f"@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}")
                    except AttributeError: pass
                if word.__contains__("@!"): # User
                    try:
                        userId = search("<@!(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        replyContent = replyContent.replace(f"<@!{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                    except AttributeError: pass
                if word.__contains__("@"): # User
                    try:
                        userId = search("<@(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userId = userId.replace("!", "")
                        replyContent = replyContent.replace(f"<@{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                    except AttributeError: pass
        except: pass

        dateTime = strftime("%m/%d/%y %I:%M%p", localtime(message.created_at.timestamp()))
        title = f"{color[0]}{msgAuthor}{color[1]}\t[blue]{dateTime}[/blue] {mid}".expandtabs((chats.size.width + color[2] - 15) - (len(str(mid)) + len(str(dateTime))))
        w = TextWrapper(width=chats.size.width-4, break_long_words=True, replace_whitespace=True)
        if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)
        
        try:
            if len(replyContent) <= 57:
                PyCordInterface.chatHistory.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {replyContent}")
            else:
                w = TextWrapper(width=chats.size.width-24, break_long_words=True, replace_whitespace=True)
                messages = [w.fill(p) for p in replyContent.splitlines()]
                messages = messages[0].split("\n")
                PyCordInterface.chatHistory.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {messages[0]}...")
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
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 attatchment.[/cyan]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.attachments)} attatchments.[/cyan]")

            await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))

        else:
            PyCordInterface.chatHistory.append(title)
            if message.attachments != []:
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                if len(message.attachments) == 1:
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 attatchment.[/cyan]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.attachments)} attatchments.[/cyan]")

            if message.embeds != []:
                if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                if len(message.embeds) == 1:
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 embed.[/cyan]")
                else:
                    PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.embeds)} embeds.[/cyan]")

            await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
        chats.refresh

bot = PyCord()
    
class PyCordInterface(App):
    token = getenv("token")
    try: Thread(target=bot.run, kwargs={"token": token}).start()
    except KeyboardInterrupt: pass

    chatHistory = []
    
    async def on_load(self) -> None:
        global pyCordReady
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
        if api["tag_name"] != "v1.4":
            tag = api["tag_name"]
            title = api["name"]
            info = api["body"]
            print( "* PyCord Update Available!\n")
            print(f"[{tag}] {title}\n{info}")
            print( "\n* Visit https://github.com/PyTsun/PyCord/releases to download update!")
        
            await aiosleep(5)
        
        print("* Checking Server List...")
        if len(bot.guilds) == 0:
            print(" Your Discord Bot is Currently on 0 Guilds. Please invite your bot to a Discord Server to continue!")
            while bot.guilds.count == 0:
                await aiosleep(1)
        print(f"* Currently on {str(len(bot.guilds))} servers")
    
        await aiosleep(1.5)
        pyCordReady = True

    async def displayHistory(self):
        await chats.update(Panel("", title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", subtitle="Loading...", subtitle_align="left", border_style="cyan", box=boxType))
        lastChannel = channelFocus[1]
        await aiosleep(1)
        if lastChannel != channelFocus[1]: return
        await chats.update(Panel("", title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style="cyan", box=boxType))
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
                                replyContent += "╰── [cyan]Sent 1 attatchment.[/cyan] "
                            else:
                                replyContent += f"╰── [cyan]Sent {len(message.reference.resolved.attachments)} attatchments.[/cyan] "

                        if message.reference.resolved.embeds != []:
                            if len(message.reference.resolved.attachments) == 1:
                                replyContent = "╰── [cyan]Sent 1 embed.[/cyan]"
                            else:
                                replyContent = f"╰── [cyan]Sent {len(message.reference.resolved.embeds)} embeds.[/cyan]"
            except: pass

            try: PyCord.typingQueue.remove(message.author.display_name)
            except: pass

            if message.guild.id != serverFocus[1]: return
            if message.channel.id != channelFocus[1]: return

            if message.author.bot:
                color = ["[blue]", "[/blue]", 23]
            else:
                color = ["[cyan]", "[/cyan]", 23]

            if message.author.id == bot.user.id:
                color = ["[green]", "[/green]", 25]

            if message.author.id == message.guild.owner.id:
                color = ["[yellow]", "[/yellow]", 27]

            try:
                if message.reference.resolved.author.bot:
                    rColor = ["[blue]", "[/blue]", 13]
                else:
                    rColor = ["[cyan]", "[/cyan]", 13]

                if message.reference.resolved.author.id == bot.user.id:
                    rColor = ["[green]", "[/green]", 15]

                if message.reference.resolved.author.id == message.guild.owner.id:
                    rColor = ["[yellow]", "[/yellow]", 17]
            except: pass

            for word in message.content.split():
                if word.__contains__("#"): # Channel
                    try:
                        channelId = search("<#(.*?)>", word).group(1)
                        msg = msg.replace(f"<#{channelId}>", f"#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}")
                    except AttributeError: pass

                if word.__contains__("@&"): # Role
                    try:
                        roleId = search("<@&(.*?)>", word).group(1)
                        msg = msg.replace(f"<@&{roleId}>", f"@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}")
                    except AttributeError: pass

                if word.__contains__("@!"): # User
                    try:
                        userId = search("<@!(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        msg = msg.replace(f"<@!{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                    except AttributeError: pass

                if word.__contains__("@"): # User
                    try:
                        userId = search("<@(.*?)>", word).group(1)
                        userId = userId.replace("&", "")
                        userId = userId.replace("!", "")
                        msg = msg.replace(f"<@{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                    except AttributeError: pass
                
            
            try:
                for word in message.reference.resolved.content.split():
                    if word.__contains__("#"): # Channel
                        try:
                            channelId = search("<#(.*?)>", word).group(1)
                            replyContent = replyContent.replace(f"<#{channelId}>", f"#{bot.get_guild(serverFocus[1]).get_channel(int(channelId)).name}")
                        except AttributeError: pass

                    if word.__contains__("@&"): # Role
                        try:
                            roleId = search("<@&(.*?)>", word).group(1)
                            replyContent = replyContent.replace(f"<@&{roleId}>", f"@{bot.get_guild(serverFocus[1]).get_role(int(roleId)).name}")
                        except AttributeError: pass

                    if word.__contains__("@!"): # User
                        try:
                            userId = search("<@!(.*?)>", word).group(1)
                            userId = userId.replace("&", "")
                            replyContent = replyContent.replace(f"<@!{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                        except AttributeError: pass

                    if word.__contains__("@"): # User
                        try:
                            userId = search("<@(.*?)>", word).group(1)
                            userId = userId.replace("&", "")
                            userId = userId.replace("!", "")
                            replyContent = replyContent.replace(f"<@{userId}>", f"@{bot.get_guild(serverFocus[1]).get_member(int(userId)).display_name}")
                        except AttributeError: pass
            except: pass

            dateTime = strftime("%m/%d/%y %I:%M%p", localtime(message.created_at.timestamp()))
            title = f"{color[0]}{msgAuthor}{color[1]}\t[blue]{dateTime}[/blue] {mid}".expandtabs((chats.size.width + color[2] - 15) - (len(str(mid)) + len(str(dateTime))))
            w = TextWrapper(width=chats.size.width-12, break_long_words=True, replace_whitespace=True)
            if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

            try:
                if len(replyContent) <= 57:
                    PyCordInterface.chatHistory.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {replyContent}")
                else:
                    w = TextWrapper(width=chats.size.width-24, break_long_words=True, replace_whitespace=True)
                    messages = [w.fill(p) for p in replyContent.splitlines()]
                    messages = messages[0].split("\n")
                    PyCordInterface.chatHistory.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {messages[0]}...")
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
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 attatchment.[/cyan]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.attachments)} attatchments.[/cyan]")

                await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style="cyan", box=boxType))

            else:
                PyCordInterface.chatHistory.append(title)
                if message.attachments != []:
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                    if len(message.attachments) == 1:
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 attatchment.[/cyan]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.attachments)} attatchments.[/cyan]")

                if message.embeds != []:
                    if len(PyCordInterface.chatHistory) >= chats.size.height - 2: PyCordInterface.chatHistory.pop(0)

                    if len(message.embeds) == 1:
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent 1 embed.[/cyan]")
                    else:
                        PyCordInterface.chatHistory.append(f"╰── [cyan]Sent {len(message.embeds)} embeds.[/cyan]")

                await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", subtitle="Retrieving Chat History...", subtitle_align="left", border_style="cyan", box=boxType))
        chats.refresh
        await chats.update(Panel("\n".join(PyCordInterface.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))

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
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))

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
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))

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
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
        
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
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))

    async def action_refresh(self):
        self.chatHistory.clear()
        bot.loop.create_task(self.displayHistory())
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
    
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
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
        chatBox._cursor_position = 0
        chatBox.value = ""
        
    show_bar = Reactive(False)
    def watch_show_bar(self, show_bar: bool) -> None:
        chInfo.animate("layout_offset_x", 0 if show_bar else -40)
        chats.animate("layout_offset_x", 40 if show_bar else 0)
        chatBox.animate("layout_offset_x", 40 if show_bar else 0)

    def action_toggleTopic(self) -> None:
        self.show_bar = not self.show_bar

    async def on_mount(self):
        global chatBox
        global chInfo
        global chats

        chatBox = TextInput()
        chInfo = Static(renderable=Panel("", title="Channel Info", border_style="cyan", box=boxType))
        chats = Static(renderable=Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style="cyan", box=boxType))
        
        self.set_interval(.2, chats.refresh)
        await self.view.dock(chatBox, edge="bottom", size=3)
        await self.view.dock(chats, edge="top", size=500)
        await self.view.dock(chInfo, edge="left", size=40, z=1)
        await chats.update(Panel("\n".join(self.chatHistory), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", title_align="left", border_style="cyan", box=boxType))
        await chInfo.update(Panel("z         - Go to Previous Channel\nx         - Go to Next     Channel\nshift + z - Go to Previous Server\nshift + x - Go to Next     Server\nr         - Reset Chat Logs\n\nPyCord Slash Commands\n/reply <message_id> <message>\n/leave", title=f"PyCord Controls", border_style="cyan", box=boxType))
        chInfo.layout_offset_x = -40
        bot.loop.create_task(self.displayHistory())
        self.chatHistory.clear()


PyCordInterface.run()
