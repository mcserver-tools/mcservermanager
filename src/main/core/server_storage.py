from dataclass.mcserver import McServer
from database.db_manager import DBManager

_storage: dict[int,None] = {}

def add(server: McServer) -> None:
    if not isinstance(server, McServer):
        raise TypeError(f"Expected McServer, got {type(server)}")

    if server.uid in _storage.keys():
        raise KeyError(f"Server {server.name} with uid {server.uid} already exists at {server.path}")

    _storage[server.uid] = server.wrapper
    DBManager.INSTANCE.add_mcserver(server)

def get(uid: int) -> McServer:
    if not isinstance(uid, int):
        raise TypeError(f"Expected int, got {type(uid)}")

    if not uid in _storage.keys():
        raise KeyError(f"Server with uid {uid} does not exist")

    srv = DBManager.INSTANCE.get_mcserver(uid)
    srv.wrapper = _storage[uid]
    return srv

def get_all() -> list[McServer]:
    servers = []
    for item in DBManager.INSTANCE.get_mcservers():
        servers.append(item)
        servers[-1].wrapper = _storage[servers[-1].uid]
    return servers

def save(mcserver: McServer) -> None:
    _storage[mcserver.uid] = mcserver.wrapper
    DBManager.INSTANCE.save_mcserver(mcserver)

def uids() -> list[int]:
    return [item for item in _storage.keys()]

for item in DBManager.INSTANCE.get_mcservers():
    _storage[item.uid] = None
