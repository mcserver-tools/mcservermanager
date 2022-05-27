from dataclasses import dataclass

@dataclass
class McServer():
    uid: int
    name: str = ""
    path: str = ""
    port: int = 25565
    max_players: int = 20
    ram: str = "4G"
    jar: str = "server.jar"
    whitelist: str = ""
    javapath: str = "java"
    dc_active: bool = False
    dc_id: int = 0
    dc_full: bool = False
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

if __name__ == "__main__":
    srv = McServer(35235235, "Test", "some/path/", 25566, 4, "3G", "paper-1.xx.jar", "Emanuel1,Pfefan", "java", False, 0, False)
    print(srv.get_start_command())
