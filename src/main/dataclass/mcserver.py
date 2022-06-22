"""Module containing the McServer dataclass and the default constants"""

from dataclasses import dataclass
from typing import Tuple

# pylint: disable=R0902, R0903

class Defaults():
    """Class containing default values for minecraft servers"""

    PORT = 25565
    MAX_PLAYERS = 20
    RAM = "4G"
    JAR = "server.jar"
    WHITELIST = ""
    JAVAPATH = "java"
    DC_ACTIVE = False
    DC_ID = 0
    DC_FULL = False

@dataclass
class McServer():
    """Dataclass representing a minecraft server"""

    uid: int
    name: str = ""
    path: str = ""
    port: int = Defaults.PORT
    max_players: int = Defaults.MAX_PLAYERS
    ram: str = Defaults.RAM
    jar: str = Defaults.JAR
    whitelist: str = Defaults.WHITELIST
    batchfile: str = ""
    javapath: str = Defaults.JAVAPATH
    dc_active: bool = Defaults.DC_ACTIVE
    dc_id: int = Defaults.DC_ID
    dc_full: bool = Defaults.DC_FULL
    wrapper = None

    def __post_init__(self):
        if not isinstance(self.uid, int):
            raise TypeError(f"uid has to be int, but is {type(self.uid)}")

    def get_start_command(self) -> Tuple[str, dict]:
        """Return a server start command and the start args"""

        cmd = f"{self.javapath} -Xmx{self.ram} -jar {self.jar} nogui"
        args = {"port": self.port, "maxp": self.max_players, "whitelist": self.whitelist}

        return cmd, args

    def _whitelist_str(self):
        return str(self.whitelist)

    def __str__(self) -> str:
        return str(self.get_start_command())
