import asyncio
import discord
from discord.ext import commands
import discord_group.bot_commands as bot_commands

import core.server_storage as server_storage

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = 'mc.', help_command = None, intents = discord.Intents.all())

        self._cogs = [bot_commands]
        for cog in self._cogs:
            cog.setup(self)

        DiscordBot.INSTANCE = self

    INSTANCE = None

    async def on_ready(self):
        print(f"{self.user} is now online")

    async def on_reaction_add(self, reaction, user):
        if user.name == "McServer-Manager":
            return
        await self.cogs["BotCommands"].on_reaction(reaction, user)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return await super().on_message(message)

        mcserver = None
        for item in server_storage.get_all().values():
            try:
                assert int(item.get("dc_id")) == message.channel.id
                mcserver = item
                break
            except Exception:
                pass

        if mcserver is not None:
            if mcserver.wrapper is not None and mcserver.get("dc_active") == 1:
                if message.content[0] != "/":
                    mcserver.wrapper.send_command("/" + message.content)
                else:
                    mcserver.wrapper.send_command(message.content)
                return

        return await super().on_message(message)

    def start_bot(self):
        token = open("token.txt", "r").readlines()[0]
        self.run(token)

    def stop(self):
        logout_fut = asyncio.run_coroutine_threadsafe(self.close(), self.loop)
        logout_fut.result()
        DiscordBot.INSTANCE = None

    def send(self, channel_id, text):
        send_fut = asyncio.run_coroutine_threadsafe(self.get_channel(channel_id).send(text), self.loop)
        send_fut.result()
