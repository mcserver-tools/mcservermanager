import os
import sys
import importlib
from PyQt6.QtWidgets import QApplication

import helpers.config_helper as config_helper
from dataclass.mcserver import McServer
import core.server_storage as server_storage
import gui.builder as guibuilder

class Manager():
    def __init__(self) -> None:
        if self.INSTANCE is None:
            wrapper_path = os.getcwd() + "/src/mcserverwrapper/"
            sys.path.append(wrapper_path)
            spec = importlib.util.spec_from_file_location("wrapper", wrapper_path + "wrapper.py")
            self.wrapper_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.wrapper_module)

            self._gui = None
            self.INSTANCE = self

    INSTANCE = None

    def setup(self):
        if not os.path.exists("./servers"):
            os.mkdir("./servers")

        try:
            servers = list(config_helper.get_setting(config_helper.FILEPATH, "servers"))
        except KeyError:
            config_helper.save_setting(config_helper.FILEPATH, "servers", [])

        for server in servers:
            name, path = list(server)
            self.add_server(name, path)

    def run(self):
        app = QApplication([])

        self._gui = guibuilder.build(self.INSTANCE)
        self._gui.show()

        app.exec()

    def add_server(self, name, path):
        server_storage.add(McServer(name, path))

    def change_server_name(self, old_name, new_name):
        if not any(item[0] == old_name for item in self.servers):
            raise Exception(f"Server {old_name} can't be found and thus can't be renamed")

        for item in self.servers:
            if item[0] == old_name:
                self.servers[self.servers.index(item)] = [new_name, item[1]]
                config_helper.save_setting(config_helper.FILEPATH, "servers", self.servers)
                return
