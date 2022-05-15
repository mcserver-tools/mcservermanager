import importlib
import os
import sys
from threading import Thread
from time import sleep

import discord_group.discord_bot
import gui.builder as guibuilder
from dataclass.mcserver import McServer
from PyQt6.QtWidgets import QApplication

import core.instances as instances
import core.server_storage as server_storage

class Manager():
    def __init__(self) -> None:
        if instances.Manager is not None:
            raise Exception("There is already a manager instance")

        wrapper_path = os.getcwd() + "/src/mcserverwrapper/"
        sys.path.append(wrapper_path)
        spec = importlib.util.spec_from_file_location("wrapper", wrapper_path + "wrapper.py")
        self.wrapper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.wrapper_module)

        instances.Manager = self

    def setup(self):
        if not os.path.exists("./servers"):
            os.mkdir("./servers")

    def run(self):
        app = QApplication([])

        guibuilder.build().show()

        Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        Thread(target=self._send_discord_logs, daemon=True).start()

        app.exec()

    def add_server(self, name, path):
        uid = instances.DBManager.get_new_uid()
        server_storage.add(McServer(uid=uid, name=name, path=path))
        instances.GUI.add_server(uid)

    def _send_discord_logs(self):
        while True:
            if instances.DiscordBot is not None:
                for item in server_storage.get_all():
                    if item.wrapper is not None and item.dc_active and item.dc_full and item.dc_id not in [0, None]:
                        while item.wrapper is not None and not item.wrapper.output_queue.empty():
                            instances.DiscordBot.send(int(item.dc_id), item.wrapper.output_queue.get())
            sleep(1)
