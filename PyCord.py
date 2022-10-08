import discord
from discord.ext import commands

import rich.box
from textual.app import App
from rich.panel import Panel
from textual.widgets import Static
from textual_inputs import TextInput

import time
from time import sleep
from threading import Thread
from os import getenv, system
from sys import exit as _exit
from dotenv import load_dotenv
from textwrap import TextWrapper
from textual.reactive import Reactive
from asyncio import sleep as aiosleep
load_dotenv(".env")

serverList = []
channelList = []

serverIndex = 0
channelIndex = 0
serverFocus = ["unknownServer", 0]
channelFocus = ["unknownChannel", 0]
pyCordReady = False

class PyCord(commands.Bot):
    messageQueue = []
    typingQueue = []
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        intents.typing = True
        super().__init__(command_prefix=[], intents=intents)

    async def setup_hook(self):
        Thread(target=PyCordInterface.run, kwargs={"log": "PyCord.log"}, daemon=True).start()

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
                    if "general" in channel.name:
                        global channelIndex
                        channelIndex = len(channelList)
                        channelFocus[0] = channel.name
                        channelFocus[1] = channel.id
                        lookforGeneral = False

        serverFocus[0] = server.name
        serverFocus[1] = server.id
        if lookforGeneral == True:
            channel = bot.get_channel(channelList[0])
            channelFocus[0] = channel.name
            channelFocus[1] = channel.id

        pyCordReady = True
        
        async def messageSender():
            while True:
                if self.messageQueue != []:
                    if not self.messageQueue[0] == "":
                        try:
                            await bot.get_channel(channelFocus[1]).send(self.messageQueue[0])
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
                            PyCordInterface.chats_content.append("* [red]Error:[/red] Failed to send message to channel.")
                            await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

                    else:
                        self.messageQueue.pop(0)
                
                await aiosleep(.1)
        
        await bot.loop.create_task(messageSender())

    async def on_guild_join(self, guild: discord.Guild):
        serverList.clear()
        for guild in bot.guilds:
            serverList.append(guild.id)

        if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 3: PyCordInterface.chats_content.pop(0)
        PyCordInterface.chats_content.append(f"* [blink]You have been added to [yellow]{guild.name}[/yellow]![/blink]")
        PyCordInterface.chatBox.placeholder = f"Message #{channelFocus[0]}"
        await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

    async def on_typing(self, channel: discord.TextChannel, user: discord.Member, when):
        if channel.guild.id != serverFocus[1]: return
        if channel.id != channelFocus[1]: return
        if user.id == bot.user.id: return

        PyCord.typingQueue.append(user.display_name)
        await aiosleep(12)
        try: self.typingQueue.remove(user.display_name)
        except: pass

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member, reactionEvent = None):
        if user.guild.id != serverFocus[1]: return
        if reaction.message.channel.id != channelFocus[1]: return
        if reaction.message.author.id != bot.user.id: return

        PyCordInterface.chats_content.append(f"[cyan]{user.display_name}[/cyan] reacted to your message with {reaction.emoji}")
        await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

    async def replyMessage(self, id: int, content: str):
        channelMessagable = bot.get_partial_messageable(channelFocus[1])
        message = channelMessagable.get_partial_message(id)
        await message.reply(content=content)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
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
        w = TextWrapper(width=PyCordInterface.chats.size.width-4, break_long_words=True, replace_whitespace=True)
        messagesb = [w.fill(p) for p in before.content.splitlines()]
        messagesa = [w.fill(p) for p in after.content.splitlines()]
        messagesb = messagesb[0].split("\n")
        messagesa = messagesa[0].split("\n")

        PyCordInterface.chats_content.append(title + " edited their message.")
        for x in range(len(messagesb)):
            if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: 
                PyCordInterface.chats_content.pop(0)
                
            PyCordInterface.chats_content.append(f"[red]{(messagesb[x])}[/red]")

        for x in range(len(messagesa)):
            if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: 
                PyCordInterface.chats_content.pop(0)
                PyCordInterface.chats_content.pop(0)
                
            PyCordInterface.chats_content.append(f"{(messagesa[x])}")

        await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        
    async def on_message(self, message: discord.Message):
        msg = message.content
        mid = message.id
        msgAuthor = message.author.display_name.encode("ascii", errors="ignore").decode()

        try:
            replyAuthor = message.reference.resolved.author.display_name
            replyContent = message.reference.resolved.content

            if replyContent == "":
                if message.reference.resolved.attachments != []:
                    if message.reference.resolved.attachments != []:
                        if len(message.reference.resolved.attachments) == 1:
                            replyContent += "[blink]Sent 1 attatchment.[/blink] "
                        else:
                            replyContent += f"[blink]Sent {len(message.reference.resolved.attachments)} attatchments.[/blink] "

                    if message.reference.resolved.embeds != []:
                        if len(message.reference.resolved.attachments) == 1:
                            replyContent = "[blink]Sent 1 embed.[/blink]"
                        else:
                            replyContent = f"[blink]Sent {len(message.reference.resolved.embeds)} embeds.[/blink]"
        except: pass
        
        try: self.typingQueue.remove(message.author.display_name)
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

        dateTime = time.strftime("%m/%d/%y %I:%M%p", time.localtime(message.created_at.timestamp()))
        title = f"{color[0]}{msgAuthor}{color[1]}\t[blink]{dateTime}[/blink] {mid}".expandtabs((PyCordInterface.chats.size.width + color[2] - 15) - (len(str(mid)) + len(str(dateTime))))
        w = TextWrapper(width=PyCordInterface.chats.size.width-4, break_long_words=True, replace_whitespace=True)
        if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)
        
        try:
            if len(replyContent) <= 57:
                PyCordInterface.chats_content.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {replyContent}")
            else:
                w = TextWrapper(width=PyCordInterface.chats.size.width-24, break_long_words=True, replace_whitespace=True)
                messages = [w.fill(p) for p in replyContent.splitlines()]
                messages = messages[0].split("\n")
                PyCordInterface.chats_content.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {messages[0]}...")
            if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)
        except: pass

        if message.content != "":
            messages = [w.fill(p) for p in msg.splitlines()]
            if "\n" in messages[0]:
                messages = messages[0].split("\n")
    
            if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: 
                PyCordInterface.chats_content.pop(0)
                PyCordInterface.chats_content.pop(0)

            PyCordInterface.chats_content.append(title)
            for x in range(len(messages)):
                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)
                PyCordInterface.chats_content.append(f"{(messages[x])}")

            if message.attachments != []:
                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                if len(message.attachments) == 1:
                    PyCordInterface.chats_content.append(f"[blink]Sent 1 attatchment.[/blink]")
                else:
                    PyCordInterface.chats_content.append(f"[blink]Sent {len(message.attachments)} attatchments.[/blink]")

            await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

        else:
            PyCordInterface.chats_content.append(title)
            if message.attachments != []:
                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                if len(message.attachments) == 1:
                    PyCordInterface.chats_content.append(f"[blink]Sent 1 attatchment.[/blink]")
                else:
                    PyCordInterface.chats_content.append(f"[blink]Sent {len(message.attachments)} attatchments.[/blink]")

            if message.embeds != []:
                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                if len(message.embeds) == 1:
                    PyCordInterface.chats_content.append(f"[blink]Sent 1 embed.[/blink]")
                else:
                    PyCordInterface.chats_content.append(f"[blink]Sent {len(message.embeds)} embeds.[/blink]")

            await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        PyCordInterface.chats.refresh

bot = PyCord()
    
class PyCordInterface(App):
    chats_content = []
    chatBox = TextInput(placeholder=f"Message Channel")
    chInfo = Static(renderable=Panel("", title="Channel Info", border_style="cyan", box=rich.box.ROUNDED))
    chats = Static(renderable=Panel("\n".join(chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]}", border_style="cyan", box=rich.box.ROUNDED))
    
    async def displayHistory(self):
        channel = bot.get_channel(channelFocus[1])
        messages = [message async for message in channel.history(limit=16)]
        messages.reverse()

        for message in messages:
            msg = message.content
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
                                replyContent += "[blink]Sent 1 attatchment.[/blink] "
                            else:
                                replyContent += f"[blink]Sent {len(message.reference.resolved.attachments)} attatchments.[/blink] "

                        if message.reference.resolved.embeds != []:
                            if len(message.reference.resolved.attachments) == 1:
                                replyContent = "[blink]Sent 1 embed.[/blink]"
                            else:
                                replyContent = f"[blink]Sent {len(message.reference.resolved.embeds)} embeds.[/blink]"
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
            
            dateTime = time.strftime("%m/%d/%y %I:%M%p", time.localtime(message.created_at.timestamp()))
            title = f"{color[0]}{msgAuthor}{color[1]}\t[blink]{dateTime}[/blink] {mid}".expandtabs((PyCordInterface.chats.size.width + color[2] - 15) - (len(str(mid)) + len(str(dateTime))))
            w = TextWrapper(width=PyCordInterface.chats.size.width-12, break_long_words=True, replace_whitespace=True)
            if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

            try:
                if len(replyContent) <= 57:
                    PyCordInterface.chats_content.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {replyContent}")
                else:
                    w = TextWrapper(width=PyCordInterface.chats.size.width-24, break_long_words=True, replace_whitespace=True)
                    messages = [w.fill(p) for p in replyContent.splitlines()]
                    messages = messages[0].split("\n")
                    PyCordInterface.chats_content.append(f"╭── {rColor[0]}{replyAuthor}{rColor[1]}: {messages[0]}...")
                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)
            except: pass

            if message.content != "":
                messages = [w.fill(p) for p in msg.splitlines()]
                if "\n" in messages[0]:
                    messages = messages[0].split("\n")

                if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: 
                    PyCordInterface.chats_content.pop(0)
                    PyCordInterface.chats_content.pop(0)

                PyCordInterface.chats_content.append(title)
                for x in range(len(messages)):
                    if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)
                    PyCordInterface.chats_content.append(f"{(messages[x])}")

                if message.attachments != []:
                    if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                    if len(message.attachments) == 1:
                        PyCordInterface.chats_content.append(f"[blink]Sent 1 attatchment.[/blink]")
                    else:
                        PyCordInterface.chats_content.append(f"[blink]Sent {len(message.attachments)} attatchments.[/blink]")

                await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

            else:
                PyCordInterface.chats_content.append(title)
                if message.attachments != []:
                    if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                    if len(message.attachments) == 1:
                        PyCordInterface.chats_content.append(f"[blink]Sent 1 attatchment.[/blink]")
                    else:
                        PyCordInterface.chats_content.append(f"[blink]Sent {len(message.attachments)} attatchments.[/blink]")

                if message.embeds != []:
                    if len(PyCordInterface.chats_content) >= PyCordInterface.chats.size.height - 2: PyCordInterface.chats_content.pop(0)

                    if len(message.embeds) == 1:
                        PyCordInterface.chats_content.append(f"[blink]Sent 1 embed.[/blink]")
                    else:
                        PyCordInterface.chats_content.append(f"[blink]Sent {len(message.embeds)} embeds.[/blink]")

                await PyCordInterface.chats.update(Panel("\n".join(PyCordInterface.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        self.chats.refresh

    async def on_load(self) -> None:
        system("title PyCord Loading...")
        await self.bind("esc", "quit", "Quit")
        await self.bind("enter", "submit", "Send Message")
        await self.bind("Z", "previousChannel", "Previous Channel")
        await self.bind("X", "nextChannel", "Next Channel")
        await self.bind("z", "previousServer", "Previous Server")
        await self.bind("x", "nextServer", "Next Server")
        await self.bind("r", "refresh", "Clear Messages")
        await self.bind("a", "toggleTopic", "Toggle Channel Topic")

        while pyCordReady == False: 
            system("cls")
            sleep(.01)
        system("title PyCord")

    async def action_previousServer(self):
        global serverIndex

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
                            if "general" in channel.name:
                                global channelIndex
                                channelIndex = len(channelList)
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False
                                
                                
                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

        self.chats_content.clear()
        bot.loop.create_task(self.displayHistory())
        self.chatBox.placeholder = f"Message #{channelFocus[0]}"
        if len(self.chats_content) >= self.chats.size.height - 2: self.chats_content.pop(0)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

    async def action_nextServer(self):
        global serverIndex

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
                            if "general" in channel.name:
                                global channelIndex
                                channelIndex = len(channelList)
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False

                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

        self.chats_content.clear()
        bot.loop.create_task(self.displayHistory())
        self.chatBox.placeholder = f"Message #{channelFocus[0]}"
        if len(self.chats_content) >= self.chats.size.height - 2: self.chats_content.pop(0)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

    async def action_previousChannel(self):
        global channelIndex

        if not channelIndex - 1 == - 1:
            channelIndex -= 1
            
            try:
                guildFocus = bot.get_channel(channelList[channelIndex])
                channelFocus[0] = guildFocus.name
                channelFocus[1] = guildFocus.id
            except: pass

        self.chats_content.clear()
        bot.loop.create_task(self.displayHistory())
        self.chatBox.placeholder = f"Message #{channelFocus[0]}"
        if len(self.chats_content) >= self.chats.size.height - 2: self.chats_content.pop(0)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        
    async def action_nextChannel(self):
        global channelIndex

        if not channelIndex >= len(channelList) - 1:
            channelIndex += 1

            try:
                guildFocus = bot.get_channel(channelList[channelIndex])
                channelFocus[0] = guildFocus.name
                channelFocus[1] = guildFocus.id
            except: pass
        
        self.chats_content.clear()
        bot.loop.create_task(self.displayHistory())
        self.chatBox.placeholder = f"Message #{channelFocus[0]}"
        if len(self.chats_content) >= self.chats.size.height - 2: self.chats_content.pop(0)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))

    async def action_refresh(self):
        self.chats_content.clear()
        self.chats_content.append("* [blink]Chat Logs Cleared and Reset.[/blink]")
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
    
    async def action_submit(self):
        if self.chatBox.value.startswith("/reply"):
            args = self.chatBox.value.split()
            id = int(args[1])
            args.pop(0)
            args.pop(0)
            content = " ".join(args)
            self.chatBox._cursor_position = 0
            self.chatBox.value = ""
            return bot.loop.create_task(PyCord.replyMessage(PyCord, id, content))

        if self.chatBox.value.startswith("/leave"):
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
                            if "general" in channel.name:
                                global channelIndex
                                channelIndex = len(channelList)
                                channelFocus[0] = channel.name
                                channelFocus[1] = channel.id
                                lookforGeneral = False

                if lookforGeneral == True:
                    channel = bot.get_channel(channelList[0])
                    channelFocus[0] = channel.name
                    channelFocus[1] = channel.id
            except: pass

            self.chatBox._cursor_position = 0
            self.chatBox.value = ""
            return bot.loop.create_task(bot.get_guild(serverFocus[1]).leave())

        PyCord.messageQueue.append(self.chatBox.value)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        self.chatBox._cursor_position = 0
        self.chatBox.value = ""

    show_bar = Reactive(False)
    def watch_show_bar(self, show_bar: bool) -> None:
        self.chInfo.animate("layout_offset_x", 0 if show_bar else -40)
        self.chats.animate("layout_offset_x", 40 if show_bar else 0)
        self.chatBox.animate("layout_offset_x", 40 if show_bar else 0)

    def action_toggleTopic(self) -> None:
        self.show_bar = not self.show_bar

    async def on_mount(self):
        self.set_interval(.2, self.chatBox.refresh)
        self.chatBox.placeholder = f"Message #{channelFocus[0]}"
        await self.view.dock(self.chatBox, edge="bottom", size=3)
        await self.view.dock(self.chats, edge="top", size=500)
        await self.view.dock(self.chInfo, edge="left", size=40, z=1)
        await self.chats.update(Panel("\n".join(self.chats_content), title=f"{serverFocus[0]} | #{channelFocus[0]} | 👥 {bot.get_guild(serverFocus[1]).member_count:,} Members", border_style="cyan", box=rich.box.ROUNDED))
        await self.chInfo.update(Panel("z         - Go to Previous Channel\nx         - Go to Next     Channel\nshift + z - Go to Previous Server\nshift + x - Go to Next     Server\nr         - Reset Chat Logs", title=f"PyCord Controls", border_style="cyan", box=rich.box.ROUNDED))
        self.chInfo.layout_offset_x = -40
        bot.loop.create_task(self.displayHistory())
        self.chats_content.clear()
try:
    token = getenv("token")
    bot.run(token)
except KeyboardInterrupt:
    _exit()
