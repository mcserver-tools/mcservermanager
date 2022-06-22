"""Module containing the BotCommands class"""

# pylint: disable=E0401, R0402

from discord.ext import commands

import core.instances as instances
import core.server_storage as server_storage

# ignore "Method could be a function",
# because I don't wanna mess with the discord bot
# pylint: disable=R0201

# ignore "Method name xx doesn't conform to snake_case",
# because the method names define the command name
# pylint: disable=C0103

class BotCommands(commands.Cog):
    """Discord Cog containing commands for the discord bot"""

    def __init__(self, client):
        self._client = client
        self._clears = []

    @commands.command()
    async def help(self, ctx):
        """Return a help command"""

        await ctx.send("This is a help command.")

    @commands.command()
    async def setuplog(self, ctx, name: str = ""):
        """Setup server logs in the current channel"""

        if name == "":
            await ctx.send(f"{ctx.message.content} <-- Missing name or uid here")
            return

        srv = None

        if name.isdigit():
            uid = int(name)
            if uid not in server_storage.uids():
                await ctx.send(f"Server with uid {uid} can't be found")
                return
            srv = server_storage.get(uid)
        else:
            try:
                srv = server_storage.get_by_name(name)
            except KeyError:
                await ctx.send(f"Server with name {name} can't be found")

        if srv is None:
            await ctx.send(f"Server {name} can't be found")
            return

        for item in server_storage.get_all():
            if item.dc_id == ctx.channel.id:
                await ctx.send(f"This channel is already initialized for {item.name} " + \
                               f"with uid {item.uid}")
                return

        srv.dc_id = ctx.channel.id
        srv.dc_active = True
        srv.dc_full = True
        server_storage.save(srv)
        if instances.GUI.active_server.uid == srv.uid:
            self._refresh_gui(srv)
        await ctx.send(f"Server logs initialized for {srv.name} with uid {srv.uid}")

    @commands.command()
    async def removelog(self, ctx, name = None):
        """Remove server logging in the current channel"""

        if name in [None, ""]:
            counter = 0
            for item in server_storage.get_all():
                if item.dc_id == ctx.channel.id:
                    item.dc_id = 0
                    item.dc_full = False
                    item.dc_active = False
                    server_storage.save(item)
                    if instances.GUI.active_server.uid == item.uid:
                        self._refresh_gui(item)
                    counter += 1
            await ctx.send(f"Removed discord logging from {counter} servers")
            return

        srv = None

        if name.isdigit():
            uid = int(name)
            if uid not in server_storage.uids():
                await ctx.send(f"Server with uid {uid} can't be found")
                return
            srv = server_storage.get(uid)
        else:
            try:
                srv = server_storage.get_by_name(name)
            except KeyError:
                await ctx.send(f"Server with name {name} can't be found")

        if srv is None:
            await ctx.send(f"Server {name} can't be found")
            return

        if srv.dc_id == 0:
            await ctx.send(f"Discord logging wasn't enabled for {name} " + \
                           f"with uid {srv.uid}, nothing changed")
            return

        srv.dc_id = 0
        srv.dc_active = False
        srv.dc_full = False
        server_storage.save(srv)
        if instances.GUI.active_server.uid == srv.uid:
            self._refresh_gui(srv)
        await ctx.send(f"Server logs removed for {srv.name} with uid {srv.uid}")

    @commands.command()
    async def clear(self, ctx, amount: int):
        """Clear amount messages in the current channel"""

        accept_decline = await ctx.send(f"Are you sure you want to delete {amount} messages?")
        yes_emoji = "✅"
        no_emoji = "❌"
        await accept_decline.add_reaction(yes_emoji)
        await accept_decline.add_reaction(no_emoji)
        self._clears.append({
            "id" : accept_decline.id,
            "amount" : amount + 2
        })

    # Disable "Unused argument"
    # pylint: disable=W0613
    async def on_reaction(self, reaction, user):
        """Overwrites default on_reaction for the clear command"""

        for i, item in enumerate(self._clears):
            if item["id"] == reaction.message.id:
                await self._clear_handler(reaction, i)
    # pylint: enable=W0613

    async def _clear_handler(self, reaction, index):
        if reaction.emoji == "✅":
            await reaction.message.channel.purge(limit=self._clears[index]["amount"])
            self._clears.pop(index)
        elif reaction.emoji == "❌":
            await reaction.message.channel.purge(limit=2)
            self._clears.pop(index)
        else:
            return

    @commands.command()
    async def UwU(self, ctx):
        """Return the gesture"""

        await ctx.send("UwU")

    def _refresh_gui(self, srv):
        instances.GUI.active_server.dc_id = srv.dc_id
        instances.GUI.active_server.dc_active = srv.dc_active
        instances.GUI.active_server.dc_full = srv.dc_full
        instances.GUI.load_profile(instances.GUI.active_server.uid)

def setup(client):
    """Setup the bot_commands cog"""

    client.add_cog(BotCommands(client))
