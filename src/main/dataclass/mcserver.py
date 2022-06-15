from dataclasses import dataclass
from typing import Tuple

class defaults():
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
    uid: int
    name: str = ""
    path: str = ""
    port: int = defaults.PORT
    max_players: int = defaults.MAX_PLAYERS
    ram: str = defaults.RAM
    jar: str = defaults.JAR
    whitelist: str = defaults.WHITELIST
    batchfile: str = ""
    javapath: str = defaults.JAVAPATH
    dc_active: bool = defaults.DC_ACTIVE
    dc_id: int = defaults.DC_ID
    dc_full: bool = defaults.DC_FULL
    wrapper = None

    def __post_init__(self):
        if not isinstance(self.uid, int):
            raise TypeError(f"uid has to be int, but is {type(self.uid)}")

    def get_start_command(self) -> Tuple[str, dict]:
        cmd = f"{self.javapath} -Xmx{self.ram} -jar {self.jar} nogui"
        args = {"port": self.port, "maxp": self.max_players, "whitelist": self.whitelist}

        return cmd, args

    def _whitelist_str(self):
        return str(self.whitelist)

    def __str__(self) -> str:
        return str(self.get_start_command())
