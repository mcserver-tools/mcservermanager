import os
from threading import Thread
from time import sleep

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QFileDialog

import core.server_storage as server_storage
import discord_group.discord_bot
import helpers.info_getter as info_getter
import core.instances as instances
from dataclass.mcserver import McServer, defaults

class GUI(QMainWindow):
    def __init__(self):
        if instances.GUI is not None:
            raise Exception("There is already a gui instance")

        super().__init__()

        self._min_size = QSize(0, 0)
        self.buttons = {}
        self.labels = {}
        self.line_edits = {}
        self.check_boxes = {}
        self.combo_boxes = {}
        self.server_list_VBox = None
        self._active_server: McServer = None

        instances.GUI = self

    def load_profile(self, uid):
        if self._active_server is not None:
            server_storage.save(self._active_server)

        for item in server_storage.uids():
            self.buttons[item].setChecked(False)
        self.buttons[uid].setChecked(True)

        self._active_server = server_storage.get(uid)
        self._load_config()

    def load_profile_lazy(self, uid):
        self._active_server = server_storage.get(uid)
        self._load_config()

    def add_server(self, uid):
        server = server_storage.get(uid)
        self.buttons[server.uid] = QPushButton(server.name + "\nstopped")
        self.buttons[server.uid].setObjectName(str(server.uid))
        self.buttons[server.uid].setFixedHeight(50)
        self.buttons[server.uid].clicked.connect(self._serverbutton_clicked)
        self.buttons[server.uid].setCheckable(True)
        self.server_list_VBox.insertWidget(self.server_list_VBox.count()-1, self.buttons[server.uid])

    def _load_config(self):
        server = self._active_server

        self._load_overview(server)
        self._load_whitelist(server)
        self._load_startup(server)
        self._load_discord(server)

        if server.wrapper is not None:
            self.buttons["start"].setText("Stop")
        else:
            self.buttons["start"].setText("Start")

    def _load_overview(self, server: McServer):
        self.line_edits["name"].setText(server.name)
        self.labels["uid"].setText(str(server.uid))
        self.labels["path"].setText(server.path)

        self.line_edits["port"].setText(str(server.port) if server.port != defaults.PORT else "")

        self.line_edits["maxplayers"].setText(str(server.max_players) if server.max_players != defaults.MAX_PLAYERS else "")

    def _load_whitelist(self, server: McServer):
        self.line_edits["whitelist"].setText(server.whitelist)

    def _load_startup(self, server: McServer):
        self.line_edits["ram"].setText(server.ram if server.ram != defaults.RAM else "")

        self.line_edits["jar"].setText(server.jar if server.jar != defaults.JAR else "")

        try:
            javaname = instances.DB_MANAGER.get_javaname(server.javapath)
            index = self.combo_boxes["java"].findText(javaname)
            if index >= 0:
                self.combo_boxes["java"].setCurrentIndex(index)
            else:
                self.combo_boxes["java"].setCurrentIndex(0)
        except (KeyError, FileNotFoundError):
            self.combo_boxes["java"].setCurrentIndex(0)

    def _load_discord(self, server: McServer):
        self.line_edits["dc_id"].setText(str(server.dc_id) if server.dc_id != defaults.DC_ID else "")

        self.check_boxes["dc_full"].setChecked(bool(server.dc_full))

        self.check_boxes["dc_active"].setChecked(bool(server.dc_active))

    def _name_changed(self, text):
        self._active_server.name = text
        instances.DB_MANAGER.add_mcserver(self._active_server)
        self.buttons[self._active_server.uid].setText(text + "\n" + self.buttons[self._active_server.uid].text().split("\n")[1])

    def _port_changed(self, text):
        try:
            self._active_server.port = int(text)
        except ValueError:
            self._active_server.port = defaults.PORT

    def _max_players_changed(self, text):
        try:
            self._active_server.max_players = int(text)
        except ValueError:
            self._active_server.max_players = defaults.MAX_PLAYERS

    def _whitelist_changed(self, text):
        self._active_server.whitelist = text if text != "" else defaults.WHITELIST

    def _ram_changed(self, text):
        self._active_server.ram = text if text != "" else defaults.RAM

    def _jar_changed(self, text):
        self._active_server.jar = text if text != "" else defaults.JAR

    def _java_changed(self, text):
        if text != "":
            self._active_server.javapath = instances.DB_MANAGER.get_javaversion(text)

    def _dcbot_toggled(self):
        if instances.DISCORD_BOT is None:
            Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        else:
            instances.DISCORD_BOT.stop()

    def _dcbot_server_toggled(self):
        self._active_server.dc_active = int(self.check_boxes["dc_active"].isChecked())

    def _dcbot_full_toggled(self):
        self._active_server.dc_full = int(self.check_boxes["dc_full"].isChecked())

    def _dcbot_id_changed(self, text):
        try:
            self._active_server.dc_id = int(text)
        except ValueError:
            self._active_server.dc_id = defaults.DC_ID

    def _serverbutton_clicked(self):
        uid = int(self.sender().objectName())
        if uid != self._active_server.uid:
            self.load_profile(uid)
        else:
            self.buttons[self._active_server.uid].setChecked(True)

    def _pathbutton_clicked(self):
        new_path = QFileDialog.getExistingDirectory(caption="Select the server folder")
        if new_path != "":
            self._active_server.path = new_path
            self.labels["path"].setText(new_path)
            server_storage.save(self._active_server)

    def _start_button_clicked(self):
        if self.buttons["start"].text() == "Start":
            Thread(target=instances.MANAGER.start_server, args=(self._active_server.uid,)).start()
        elif self.buttons["start"].text() == "Stop":
            Thread(target=instances.MANAGER.stop_server, args=(self._active_server.uid,)).start()
        else:
            raise Exception(f"start_button is in false state {self.buttons['start'].text()}")

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
