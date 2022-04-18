

class McServer():
    def __init__(self, attributes: dict) -> None:
        self._attributes = {}

        for key in attributes.keys():
            if key not in self._valid_keys:
                raise KeyError(f"Invalid key {key}")
            self._attributes[key] = attributes[key]

    _valid_keys = ["name", "port", "status", "players", "whitelist"]

    def set(self, key, value):
        if key not in self._valid_keys:
                raise KeyError(f"Invalid key {key}")

        self._attributes[key] = value

    def get(self, key):
        if key not in self._valid_keys:
            raise KeyError(f"Invalid key {key}")

        return self._attributes[key]

    def __str__(self) -> str:
        return str(self._attributes)

# every minecraft server has static (not changing while running): 
# port, name, version, 

# every minecraft server has dynamic (changing while running): 
# players, 

# values changable by the user: 
# port, name, whitelisted players, 
