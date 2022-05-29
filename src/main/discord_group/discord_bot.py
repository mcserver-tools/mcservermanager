import asyncio
import cmd
import discord
from discord.ext import commands
import discord_group.bot_commands as bot_commands

import core.server_storage as server_storage
import core.instances as instances

class DiscordBot(commands.Bot):
    def __init__(self):
        if instances.DiscordBot is not None:
            raise Exception("There is already a discordbot instance")

        super().__init__(command_prefix = 'mc.', help_command = None, intents = discord.Intents.all())

        self._messages = {}

        self._cogs = [bot_commands]
        for cog in self._cogs:
            cog.setup(self)

    async def on_ready(self):
        instances.DiscordBot = self
        print(f"{self.user} is now online")

    async def on_reaction_add(self, reaction, user):
        if user.name == "McServer-Manager":
            return
        await self.cogs["BotCommands"].on_reaction(reaction, user)

    async def on_message(self, message):
        if message.author.id == self.user.id or message.content.startswith("mc."):
            return await super().on_message(message)

        mcserver = None
        for item in server_storage.get_all():
            if item.dc_id == message.channel.id:
                mcserver = item

        if mcserver is not None and mcserver.dc_active == 1:
            if mcserver.wrapper is None:
                if message.content.strip("/") == "start":
                    instances.Manager.start_server(mcserver.uid)
            else:
                if message.content.strip("/") == "stop":
                    instances.Manager.stop_server(mcserver.uid)
                elif message.content[0] != "/":
                    mcserver.wrapper.send_command("/" + message.content)
                else:
                    mcserver.wrapper.send_command(message.content)
            return

    def start_bot(self):
        token = open("token.txt", "r").readlines()[0]
        self.run(token)

    def stop(self):
        logout_fut = asyncio.run_coroutine_threadsafe(self.close(), self.loop)
        logout_fut.result()
        DiscordBot.INSTANCE = None

    def send(self, channel_id, text):
        if channel_id in self._messages.keys() and len(self._messages[channel_id].content) + 2 + len(text) < 2000:
            new_text = f"{self._messages[channel_id].content}\n{text}"
            edit_fut = asyncio.run_coroutine_threadsafe(self._messages[channel_id].edit(content=new_text), self.loop)
            edit_fut.result()
        else:
            send_fut = asyncio.run_coroutine_threadsafe(self.get_channel(channel_id).send(text), self.loop)
            self._messages[channel_id] = send_fut.result()
