from dataclasses import dataclass

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
    javapath: str = defaults.JAVAPATH
    dc_active: bool = defaults.DC_ACTIVE
    dc_id: int = defaults.DC_ID
    dc_full: bool = defaults.DC_FULL
    wrapper = None

    def __post_init__(self):
        if not isinstance(self.uid, int):
            raise TypeError(f"uid has to be int, but is {type(self.uid)}")

    def get_start_command(self) -> str:
        params = [("jar", self.jar), ("ram", self.ram), ("port", self.port), ("maxp", self.max_players), ("whitelist", self._whitelist_str())]
        cmd = f'-java "{self.javapath}"'

        for param in params:
            try:
                cmd += f" -{param[0]} {param[1]}" if param[1] != "" else ""
            except KeyError:
                pass
        return cmd.strip(" ")

    def _whitelist_str(self):
        return str(self.whitelist)

    def __str__(self) -> str:
        return f'name "{self.name}", path "{self.path}", uid "{self.uid}", {self.get_start_command().replace(" -", ", ")[1::]}'
