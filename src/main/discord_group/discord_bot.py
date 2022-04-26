import asyncio
import discord
from discord.ext import commands
import discord_group.bot_commands as bot_commands

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
        await self._cogs["BotCommands"].on_reaction(reaction, user)

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
