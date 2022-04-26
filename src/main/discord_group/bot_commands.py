from discord.ext import commands

class BotCommands(commands.Cog):
    def __init__(self, client):
        self._client = client
        self._clears = []

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

def setup(client):
    client.add_cog(BotCommands(client))
