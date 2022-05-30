from discord.ext import commands

import core.instances as instances
import core.server_storage as server_storage

class BotCommands(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._clears = []

    @commands.command()
    async def help(self, ctx):
        await ctx.send("This is a help command.")

    @commands.command()
    async def setuplog(self, ctx, name: str = ""):
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
            except:
                await ctx.send(f"Server with name {name} can't be found")
        
        if srv is None:
            await ctx.send(f"Server {name} can't be found")
            return

        for item in server_storage.get_all():
            if item.dc_id == ctx.channel.id:
                await ctx.send(f"This channel is already initialized for {item.name} with uid {item.uid}")
                return

        srv.dc_id = ctx.channel.id
        srv.dc_active = True
        srv.dc_full = True
        server_storage.save(srv)
        if instances.GUI._active_server.uid == srv.uid:
            self._refresh_gui(srv)
        await ctx.send(f"Server logs initialized for {srv.name} with uid {srv.uid}")

    @commands.command()
    async def removelog(self, ctx, name = None):
        if name in [None, ""]:
            c = 0
            for item in server_storage.get_all():
                if item.dc_id == ctx.channel.id:
                    item.dc_id = 0
                    item.dc_full = False
                    item.dc_active = False
                    server_storage.save(item)
                    if instances.GUI._active_server.uid == item.uid:
                        self._refresh_gui(item)
                    c += 1
            await ctx.send(f"Removed discord logging from {c} servers")
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
            except:
                await ctx.send(f"Server with name {name} can't be found")
        
        if srv is None:
            await ctx.send(f"Server {name} can't be found")
            return

        if srv.dc_id == 0:
            await ctx.send(f"Discord logging wasn't enabled for {name} with uid {srv.uid}, nothing changed")
            return

        srv.dc_id = 0
        srv.dc_active = False
        srv.dc_full = False
        server_storage.save(srv)
        if instances.GUI._active_server.uid == srv.uid:
            self._refresh_gui(srv)
        await ctx.send(f"Server logs removed for {srv.name} with uid {srv.uid}")

    @commands.command()
    async def clear(self, ctx, amount: int):
        accept_decline = await ctx.send(f"Are you sure you want to delete {amount} messages?")
        yes_emoji = "✅"
        no_emoji = "❌"
        await accept_decline.add_reaction(yes_emoji)
        await accept_decline.add_reaction(no_emoji)
        self._clears.append({
            "id" : accept_decline.id,
            "amount" : amount + 2
        })

    async def on_reaction(self, reaction, user):
        for i, item in enumerate(self._clears):
            if item["id"] == reaction.message.id:
                await self._clear_handler(reaction, i)

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
        await ctx.send("UwU")

    def _refresh_gui(self, srv):
        instances.GUI._active_server.dc_id = srv.dc_id
        instances.GUI._active_server.dc_active = srv.dc_active
        instances.GUI._active_server.dc_full = srv.dc_full
        instances.GUI.load_profile(instances.GUI._active_server.uid)

def setup(client):
    client.add_cog(BotCommands(client))
