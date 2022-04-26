import os
from threading import Thread
from time import sleep

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow

import discord_group.discord_bot
import core.server_storage as server_storage
import helpers.info_getter as info_getter
from dataclass.mcserver import McServer

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
        self._active_server = server
        self._load_config()

    def _load_config(self):
        server = server_storage.get(self._active_server.name)

        self.line_edits["name"].setText(self._active_server.name)
        self.labels["path"].setText(self._active_server.path)

        try:
            self.line_edits["port"].setText(server.get("port"))
        except (KeyError, FileNotFoundError):
            self.line_edits["port"].setText("")

        try:
            self.line_edits["maxplayers"].setText(server.get("maxp"))
        except (KeyError, FileNotFoundError):
            self.line_edits["maxplayers"].setText("")

        try:
            self.line_edits["whitelist"].setText(server.get("whitelist"))
        except (KeyError, FileNotFoundError):
            self.line_edits["whitelist"].setText("")

        try:
            self.line_edits["ram"].setText(server.get("ram"))
        except (KeyError, FileNotFoundError):
            self.line_edits["ram"].setText("")

        try:
            self.line_edits["jar"].setText(server.get("jar"))
        except (KeyError, FileNotFoundError):
            self.line_edits["jar"].setText("")

        try:
            self.line_edits["java"].setText(server.get("java"))
        except (KeyError, FileNotFoundError):
            self.line_edits["java"].setText("")

        try:
            self.line_edits["dc_id"].setText(server.get("dc_id"))
        except (KeyError, FileNotFoundError):
            self.line_edits["dc_id"].setText("")

        try:
            self.check_boxes["dc_full"].setChecked(bool(server.get("dc_full")))
        except (KeyError, FileNotFoundError):
            self.check_boxes["dc_full"].setChecked(False)

        try:
            self.check_boxes["dc_active"].setChecked(bool(server.get("dc_active")))
        except (KeyError, FileNotFoundError):
            self.check_boxes["dc_active"].setChecked(False)

        if server.wrapper is not None:
            self.buttons["start"].setText("Stop")
        else:
            self.buttons["start"].setText("Start")

    def _name_changed(self, text):
        server_storage.rename(self._active_server.name, text)
        self.buttons[text] = self.buttons.pop(self._active_server.name)
        self.buttons[text].setText(text + "\n" + self.buttons[text].text().split("\n")[1])
        self._active_server = server_storage.get(text)

    def _port_changed(self, text):
        server_storage.get(self._active_server.name).set("port", text)

    def _max_players_changed(self, text):
        server_storage.get(self._active_server.name).set("maxp", text)

    def _whitelist_changed(self, text):
        server_storage.get(self._active_server.name).set("whitelist", text)

    def _ram_changed(self, text):
        server_storage.get(self._active_server.name).set("ram", text)

    def _jar_changed(self, text):
        server_storage.get(self._active_server.name).set("jar", text)

    def _java_changed(self, text):
        server_storage.get(self._active_server.name).set("java", text)

    def _dcbot_toggled(self):
        if discord_group.discord_bot.DiscordBot.INSTANCE is None:
            Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        else:
            discord_group.discord_bot.DiscordBot.INSTANCE.stop()

    def _dcbot_server_toggled(self):
        server_storage.get(self._active_server.name).set("dc_active", int(self.check_boxes["dc_active"].isChecked()))

    def _dcbot_full_toggled(self):
        server_storage.get(self._active_server.name).set("dc_full", int(self.check_boxes["dc_full"].isChecked()))

    def _dcbot_id_changed(self, text):
        server_storage.get(self._active_server.name).set("dc_id", text)

    def _button_clicked(self):
        servername = self.sender().objectName()
        if servername != self._active_server.name:
            self.buttons[self._active_server.name].setChecked(False)
            self.load_profile(server_storage.get(servername))

    def _start_button_clicked(self):
        if self.buttons["start"].text() == "Start":
            Thread(target=self._start_server).start()
        elif self.buttons["start"].text() == "Stop":
            Thread(target=self._stop_server).start()
        else:
            raise Exception(f"start_button is in false state {self.buttons['start'].text()}")

    def _start_server(self):
        server_name = self._active_server.name
        server = server_storage.get(server_name)
        cmd = server.get_start_command()

        self.buttons[server_name].setText(server_name + "\nstarting...")

        print(f"Starting {server_name} with the following args:")
        print(cmd)

        main_cwd = os.getcwd()
        os.chdir(server.path)
        server.wrapper = GUI.MANAGER.wrapper_module.Wrapper(output=False, args=cmd)
        server.wrapper.startup()
        os.chdir(main_cwd)

        self.buttons[server_name].setText(server_name + f"\nonline (0/{server.get('maxp')})")
        self.buttons["start"].setText("Stop")

    def _stop_server(self):
        server_name = self._active_server.name
        server = server_storage.get(server_name)

        self.buttons[server_name].setText(server_name + "\nstopping...")

        server.wrapper.stop()
        sleep(5)

        server.wrapper = None
        self.buttons[server_name].setText(server_name + f"\nstopped")
        self.buttons["start"].setText("Start")

    def _update_players_thread(self):
        while True:
            for server in server_storage.get_all().values():
                if server.wrapper is not None:
                    self._handle_server(server)
            sleep(3)

    def _handle_server(self, server):
        status = info_getter.ping_address_with_return("127.0.0.1", server.get("port"))
        if status is not None:
            old_text = self.buttons[server.name].text()
            if "starting..." in old_text or "stopping..." in old_text:
                return
            split_text = old_text.split("(")
            new_text = f"{split_text[0]}({status.players.online}/{split_text[1].split('/')[1]}"
            self.buttons[server.name].setText(new_text)
