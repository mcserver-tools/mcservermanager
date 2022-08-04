import core.server_storage as server_storage
from dataclass.mcserver import McServer

def get_server(input_var: str) -> McServer | None:
    """Search for a local server with the given input"""

    # try to use the input_var as an uid
    if input_var.isdigit():
        uid = int(input_var)
        if uid in server_storage.uids():
            return server_storage.get(uid)

    # try to use the input_var as a server name
    try:
        return server_storage.get_by_name(input_var)
    # the server couldn't be found, ignore the exception
    except KeyError:
        pass
    return None

def get_address(input_var: str) -> tuple[str, int]:
    """Get (address, port) from the given input"""

    srv = get_server(input_var)
    if srv:
        return ("127.0.0.1", srv.port)
    
    # parse the input_var to an hostname/port
    if len(input_var.split(":")) == 2:
        input_var_split = input_var.split(":")
        return (input_var_split[0], input_var_split[1])
    if len(input_var.split(" ")) == 2:
        input_var_split = input_var.split(" ")
        return (input_var_split[0], input_var_split[1])
    return (input_var, 25565)

def get_dc_channel_server(ctx) -> McServer | None:
    """Get McServer from the given discord context"""

    # try to find server linked to the discord channel
    for item in server_storage.get_all():
        if item.dc_id == ctx.channel.id:
            return item
    return None

def get_dc_channel_servers(ctx) -> list[McServer] | None:
    """Get McServers from the given discord context"""

    servers = []
    # try to find servers linked to the discord channel
    for item in server_storage.get_all():
        if item.dc_id == ctx.channel.id:
            servers.append(item)

    return servers if len(servers) > 0 else None
