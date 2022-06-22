"""Module containing a function to ping a server with returns"""

from mcstatus import JavaServer
from mcstatus.pinger import PingResponse

def ping_address_with_return(address, port) -> PingResponse | None:
    """Return a PingResponse if the server is pingable, else return None"""

    if isinstance(port, str):
        port = int(port)
    try:
        server = JavaServer(address, port)
        status = server.status()
        return status
    except (TimeoutError, ConnectionAbortedError, ConnectionResetError, IOError):
        return None
    except KeyError as keyerr:
        if "text" in keyerr.args or "#" in keyerr.args:
            print("Retrying...")
            return ping_address_with_return(address, port)
    except IndexError as indexerr:
        if "bytearray" in indexerr.args:
            print("Retrying...")
            return ping_address_with_return(address, port)
    return None
