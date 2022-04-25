from mcserver import McServer

_storage = {}

def add(server: McServer) -> None:
    if not isinstance(server, McServer):
        raise TypeError(f"Expected McServer, got {type(server)}")

    if server.name in _storage.keys():
        raise KeyError(f"Server with key {server.name} already exists at {server.path}")

    _storage[server.name] = server

def get(name: str) -> McServer:
    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name)}")

    return _storage[name]

def keys() -> list[str]:
    return list(_storage.keys())

def rename(old_name: str, new_name: str):
    if not isinstance(old_name, str):
        raise TypeError(f"Expected str, got {type(old_name)}")
    if not isinstance(new_name, str):
        raise TypeError(f"Expected str, got {type(new_name)}")

    _storage[new_name] = _storage.pop(old_name)
    _storage[new_name].name = new_name