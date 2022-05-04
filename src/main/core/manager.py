import importlib
import os
import sys
from threading import Thread
from time import sleep

import discord_group.discord_bot
import gui.builder as guibuilder
from database.db_manager import DBManager
from dataclass.mcserver import McServer
from PyQt6.QtWidgets import QApplication

import core.server_storage as server_storage

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

    def run(self):
        app = QApplication([])

        self._gui = guibuilder.build(self.INSTANCE)
        self._gui.show()

        Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        Thread(target=self._send_discord_logs, daemon=True).start()

        app.exec()

    def add_server(self, name, path):
        server_storage.add(McServer(uid=DBManager.INSTANCE.get_new_uid(), name=name, path=path))

    def _send_discord_logs(self):
        while True:
            if discord_group.discord_bot.DiscordBot.INSTANCE is not None:
                for item in server_storage.get_all():
                    if item.wrapper is not None and item.dc_active and item.dc_full and item.dc_id not in [0, None]:
                        while item.wrapper is not None and not item.wrapper.output_queue.empty():
                            discord_group.discord_bot.DiscordBot.INSTANCE.send(int(item.dc_id), item.wrapper.output_queue.get())
            sleep(1)
