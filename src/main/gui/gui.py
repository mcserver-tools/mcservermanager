import os
from threading import Thread
from time import sleep

import core.server_storage as server_storage
import discord_group.discord_bot
import helpers.info_getter as info_getter
from database.db_manager import DBManager
from dataclass.mcserver import McServer
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow

class GUI(QMainWindow):
    def __init__(self, manager):
        super().__init__()

        self._min_size = QSize(0, 0)
        self.buttons = {}
        self.labels = {}
        self.line_edits = {}
        self.check_boxes = {}
        self._active_server: McServer = None
        GUI.MANAGER = manager
        GUI.INSTANCE = self

    MANAGER = None
    INSTANCE = None

    def load_profile(self, server):
        if self._active_server is not None:
            server_storage.save(self._active_server)
        self._active_server = server
        self._load_config()

    def _load_config(self):
        server = server_storage.get(self._active_server.uid)

        self.line_edits["name"].setText(self._active_server.name)
        self.labels["path"].setText(self._active_server.path)

        try:
            self.line_edits["port"].setText(str(server.port) if server.port != 25565 else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["port"].setText("")

        try:
            self.line_edits["maxplayers"].setText(str(server.max_players) if server.max_players != 20 else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["maxplayers"].setText("")

        try:
            self.line_edits["whitelist"].setText(server.whitelist)
        except (KeyError, FileNotFoundError):
            self.line_edits["whitelist"].setText("")

        try:
            self.line_edits["ram"].setText(server.ram if server.ram != "4G" else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["ram"].setText("")

        try:
            self.line_edits["jar"].setText(server.jar if server.jar != "server.jar" else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["jar"].setText("")

        try:
            self.line_edits["java"].setText(server.javapath if server.javapath != "java" else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["java"].setText("")

        try:
            self.line_edits["dc_id"].setText(str(server.dc_id) if server.dc_id != 0 else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["dc_id"].setText("")

        try:
            self.check_boxes["dc_full"].setChecked(bool(server.dc_full))
        except (KeyError, FileNotFoundError):
            self.check_boxes["dc_full"].setChecked(False)

        try:
            self.check_boxes["dc_active"].setChecked(bool(server.dc_active))
        except (KeyError, FileNotFoundError):
            self.check_boxes["dc_active"].setChecked(False)

        if server.wrapper is not None:
            self.buttons["start"].setText("Stop")
        else:
            self.buttons["start"].setText("Start")

    def _name_changed(self, text):
        self._active_server.name = text
        DBManager.INSTANCE.add_mcserver(self._active_server)
        self.buttons[self._active_server.uid].setText(text + "\n" + self.buttons[self._active_server.uid].text().split("\n")[1])

    def _port_changed(self, text):
        self._active_server.port = text

    def _max_players_changed(self, text):
        self._active_server.max_players = text

    def _whitelist_changed(self, text):
        self._active_server.whitelist = text

    def _ram_changed(self, text):
        self._active_server.ram = text

    def _jar_changed(self, text):
        self._active_server.jar = text

    def _java_changed(self, text):
        self._active_server.java = text

    def _dcbot_toggled(self):
        if discord_group.discord_bot.DiscordBot.INSTANCE is None:
            Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        else:
            discord_group.discord_bot.DiscordBot.INSTANCE.stop()

    def _dcbot_server_toggled(self):
        self._active_server.dc_active = int(self.check_boxes["dc_active"].isChecked())

    def _dcbot_full_toggled(self):
        self._active_server.dc_full = int(self.check_boxes["dc_full"].isChecked())

    def _dcbot_id_changed(self, text):
        self._active_server.dc_id = text

    def _button_clicked(self):
        serveruid = int(self.sender().objectName())
        if serveruid != self._active_server.uid:
            self.buttons[self._active_server.uid].setChecked(False)
            self.load_profile(server_storage.get(serveruid))
        else:
            self.buttons[self._active_server.uid].setChecked(True)

    def _start_button_clicked(self):
        if self.buttons["start"].text() == "Start":
            Thread(target=self._start_server).start()
        elif self.buttons["start"].text() == "Stop":
            Thread(target=self._stop_server).start()
        else:
            raise Exception(f"start_button is in false state {self.buttons['start'].text()}")

    def _start_server(self):
        cmd = self._active_server.get_start_command()

        self.buttons[self._active_server.uid].setText(f"{self._active_server.name}\nstarting...")

        print(f"Starting {self._active_server.name} with the following args:")
        print(cmd)

        main_cwd = os.getcwd()
        os.chdir(self._active_server.path)
        self._active_server.wrapper = GUI.MANAGER.wrapper_module.Wrapper(output=False, args=cmd)
        server_storage.save(self._active_server)
        self._active_server.wrapper.startup()
        os.chdir(main_cwd)

        self.buttons[self._active_server.uid].setText(f"{self._active_server.name}\nonline (0/{self._active_server.max_players})")
        self.buttons["start"].setText("Stop")

    def _stop_server(self):
        server = server_storage.get(self._active_server.uid)

        self.buttons[self._active_server.uid].setText(f"{self._active_server.name}\nstopping...")

        server.wrapper.stop()
        sleep(5)

        server.wrapper = None
        self.buttons[self._active_server.uid].setText(f"{self._active_server.name}\nstopped")
        self.buttons["start"].setText("Start")

        server_storage.save(self._active_server)

    def _update_players_thread(self):
        while True:
            for server in server_storage.get_all():
                if server.wrapper is not None:
                    self._handle_server(server)
            sleep(3)

    def _handle_server(self, server):
        status = info_getter.ping_address_with_return("127.0.0.1", server.port)
        if status is not None:
            old_text = self.buttons[server.uid].text()
            if "starting..." in old_text or "stopping..." in old_text:
                return
            split_text = old_text.split("(")
            new_text = f"{split_text[0]}({status.players.online}/{split_text[1].split('/')[1]}"
            self.buttons[server.uid].setText(new_text)
