import core.instances as instances
from dataclass.mcserver import McServer

_storage: dict[int,None] = {}

def add(server: McServer) -> None:
    if not isinstance(server, McServer):
        raise TypeError(f"Expected McServer, got {type(server)}")

    if server.uid in _storage.keys():
        raise KeyError(f"Server {server.name} with uid {server.uid} already exists at {server.path}")

    _storage[server.uid] = server.wrapper
    instances.DBManager.add_mcserver(server)

def get(uid: int) -> McServer:
    if not isinstance(uid, int):
        raise TypeError(f"Expected int, got {type(uid)}")

    if not uid in _storage.keys():
        raise KeyError(f"Server with uid {uid} does not exist")

    srv = instances.DBManager.get_mcserver(uid)
    srv.wrapper = _storage[uid]
    return srv

def get_by_name(name: str) -> McServer:
    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name)}")

    srv = instances.DBManager.get_mcserver_by_name(name)
    srv.wrapper = _storage[srv.uid]
    return srv

def get_all() -> list[McServer]:
    servers = []
    for item in instances.DBManager.get_mcservers():
        servers.append(item)
        servers[-1].wrapper = _storage[servers[-1].uid]
    return servers

def save(mcserver: McServer) -> None:
    _storage[mcserver.uid] = mcserver.wrapper
    instances.DBManager.save_mcserver(mcserver)

def setup():
    for item in instances.DBManager.get_mcservers():
        _storage[item.uid] = None

def remove(uid: int) -> None:
    instances.DBManager.remove_mcserver(uid)
    del _storage[uid]

def uids() -> list[int]:
    return [item for item in _storage.keys()]
