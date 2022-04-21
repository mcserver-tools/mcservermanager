import os
from PyQt6.QtWidgets import QApplication

import config_helper
from gui import GUI

class Manager():
    def __init__(self) -> None:
        if self.INSTANCE is None:
            self.servers = []
            self.wrapper_path = "mcserverwrapper"
            self._gui = None
            self.INSTANCE = self

    INSTANCE = None

    def setup(self):
        if os.system(f"where {self.wrapper_path}") == 1:
            self.wrapper_path = os.path.join(os.getcwd(), "mcserverwrapper/mcserverwrapper.bat")

        if not os.path.exists("./servers"):
            os.mkdir("./servers")

        try:
            config_helper.get_setting(config_helper.FILEPATH, "servers")
        except KeyError:
            config_helper.save_setting(config_helper.FILEPATH, "servers", [])

    def run(self):
        app = QApplication([])

        self._gui = GUI(self.INSTANCE)
        self._gui.setup()
        self._gui.show()

        app.exec()

    def add_server(self, name, path):
        oldservers = config_helper.get_setting(config_helper.FILEPATH, "servers")
        try:
            self.servers = list(oldservers)
        except Exception as e:
            print(e)

        if not any(item[0] == name for item in self.servers):
            self.servers.append((name, path))
        else:
            for item in self.servers:
                if item[0] == name:
                    self.servers[self.servers.index(item)] = (name, path)

        config_helper.save_setting(config_helper.FILEPATH, "servers", self.servers)

    def change_server_name(self, old_name, new_name):
        if not any(item[0] == old_name for item in self.servers):
            raise Exception(f"Server {old_name} can't be found and thus can't be renamed")

        for item in self.servers:
            if item[0] == old_name:
                self.servers[self.servers.index(item)] = [new_name, item[1]]
                config_helper.save_setting(config_helper.FILEPATH, "servers", self.servers)
                return
