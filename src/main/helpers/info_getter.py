"""Module containing a function to ping a server with returns"""

import logging
from mcstatus import JavaServer
from mcstatus.pinger import PingResponse

from dataclass.mcstatus import McStatus

def ping_address_with_return(address, port, tries: int = 3) -> McStatus | None:
    """Return a McStatus if the server is pingable, else return None"""

    logging.debug(f"Pinging {address}:{port} for info")

    if isinstance(port, str):
        port = int(port)

    while tries > 0:
        status = _get_status(address, port)
        if status:
            return McStatus.from_pingresponse(status, (address, port))
        tries -= 1

    return None

def get_players(address, port) -> list[str] | None:
    """Return a list containing all of the online players, or None if the server is unreachable"""

    logging.debug(f"Pinging {address}:{port} for players")
    if isinstance(port, str):
        port = int(port)

    response = _get_status(address, port)
    if not response:
        return None

    total_players = response.players.online
    if total_players == 0 or not response.players.sample or len(response.players.sample) == 0:
        return []

    player_names = [item.name for item in response.players.sample]
    tries = 50
    while tries > 0:
        tries -= 1

        response = _get_status(address, port)
        if not response:
            logging.debug(f"Server {address}:{port} went not reachable during player gathering")
            return player_names

        sample = [item.name for item in response.players.sample]
        player_names += list(set(sample) - set(player_names))

        if len(player_names) >= total_players:
            return player_names
    return player_names

def _get_status(address: str, port: int) -> PingResponse | None:
    try:
        server = JavaServer(address, port)
        return server.status()
    except (TimeoutError, ConnectionAbortedError, ConnectionResetError, IOError):
        return None
    except KeyError as keyerr:
        if "text" in keyerr.args or "#" in keyerr.args:
            return None
    except IndexError as indexerr:
        if "bytearray" in indexerr.args:
            return None
