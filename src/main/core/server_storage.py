"""Module containing I/O functions to the database"""

# pylint: disable=E0401, R0402

import core.instances as instances
from dataclass.mcserver import McServer

_storage: dict[int,None] = {}

def add(server: McServer) -> None:
    """Add a server to the database"""

    if not isinstance(server, McServer):
        raise TypeError(f"Expected McServer, got {type(server)}")

    if server.uid in _storage:
        raise KeyError(f"Server {server.name} with uid {server.uid} " + \
                       f"already exists at {server.path}")

    _storage[server.uid] = server.wrapper
    instances.DB_MANAGER.add_mcserver(server)

def get(uid: int) -> McServer:
    """Return a server from the database"""

    if not isinstance(uid, int):
        raise TypeError(f"Expected int, got {type(uid)}")

    if not uid in _storage:
        raise KeyError(f"Server with uid {uid} does not exist")

    srv = instances.DB_MANAGER.get_mcserver(uid)
    srv.wrapper = _storage[uid]
    return srv

def get_by_name(name: str) -> McServer:
    """Return a server withthe given name from the database"""

    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name)}")

    srv = instances.DB_MANAGER.get_mcserver_by_name(name)
    srv.wrapper = _storage[srv.uid]
    return srv

def get_all() -> list[McServer]:
    """Return all servers from the database"""

    servers = []
    for item in instances.DB_MANAGER.get_mcservers():
        servers.append(item)
        servers[-1].wrapper = _storage[servers[-1].uid]
    return servers

def save(mcserver: McServer) -> None:
    """Save a server to the database"""

    _storage[mcserver.uid] = mcserver.wrapper
    instances.DB_MANAGER.save_mcserver(mcserver)

def setup():
    """Initialize the server_storage"""

    for item in instances.DB_MANAGER.get_mcservers():
        _storage[item.uid] = None

def remove(uid: int) -> None:
    """Remove a server from the database"""

    instances.DB_MANAGER.remove_mcserver(uid)
    del _storage[uid]

def uids() -> list[int]:
    """Return all UIDs"""

    return list(_storage.keys())
