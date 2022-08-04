"""Module containing the McStatus dataclass"""

# needed for "-> McStatus:"
from __future__ import annotations

from dataclasses import dataclass

from discord import Embed
from mcstatus.pinger import PingResponse

@dataclass
class McStatus():
    """Dataclass representing the current status of a minecraft server"""

    address: tuple[str, int]
    ping: float
    version: str
    online_players: int

    @classmethod
    def from_pingresponse(cls, status: PingResponse, address: tuple[str, int]) -> McStatus:
        """Construct a McStatus from a PingResponse"""
        
        return cls(address, status.latency, status.version.name, status.players.online)

    def embed(self, title: str, players: list[str] = None) -> Embed:
        """Return the data object as an discord embed"""

        embed_var = Embed(title=title, color=0x00ff00)
        embed_var.add_field(name="Address", value=f"{self.address[0]}:{self.address[1]}",
                           inline=False)
        embed_var.add_field(name="Ping", value=f"{self.ping} ms", inline=False)
        embed_var.add_field(name="Version", value=f"{self.version[:128:]}", inline=False)
        embed_var.add_field(name="Online players", value=f"{self.online_players}", inline=False)
        if players:
            embed_var.add_field(name="Players", value=f"{str(players)}", inline=False)
        return embed_var

    def __str__(self) -> str:
        return f"Address: {self.address}, Ping: {self.ping}, Version: {self.version},\
                 Online players: {self.online_players}"
