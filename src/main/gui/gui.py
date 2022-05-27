import os
from threading import Thread
from time import sleep

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QFileDialog

import core.server_storage as server_storage
import discord_group.discord_bot
import helpers.info_getter as info_getter
import core.instances as instances
from dataclass.mcserver import McServer

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

    def load_profile(self, server):
        if self._active_server is not None:
            server_storage.save(self._active_server)
        self._active_server = server
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

        try:
            self.line_edits["port"].setText(str(server.port) if server.port != 25565 else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["port"].setText("")

        try:
            self.line_edits["maxplayers"].setText(str(server.max_players) if server.max_players != 20 else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["maxplayers"].setText("")

    def _load_whitelist(self, server: McServer):
        try:
            self.line_edits["whitelist"].setText(server.whitelist)
        except (KeyError, FileNotFoundError):
            self.line_edits["whitelist"].setText("")

    def _load_startup(self, server: McServer):
        try:
            self.line_edits["ram"].setText(server.ram if server.ram != "4G" else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["ram"].setText("")

        try:
            self.line_edits["jar"].setText(server.jar if server.jar != "server.jar" else "")
        except (KeyError, FileNotFoundError):
            self.line_edits["jar"].setText("")

        try:
            javaname = instances.DBManager.get_javaname(server.javapath)
            index = self.combo_boxes["java"].findText(javaname)
            if index >= 0:
                self.combo_boxes["java"].setCurrentIndex(index)
            else:
                self.combo_boxes["java"].setCurrentIndex(0)
        except (KeyError, FileNotFoundError):
            self.combo_boxes["java"].setCurrentIndex(0)

    def _load_discord(self, server: McServer):
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

    def _name_changed(self, text):
        self._active_server.name = text
        instances.DBManager.add_mcserver(self._active_server)
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
        if text != "":
            self._active_server.javapath = instances.DBManager.get_javaversion(text)

    def _dcbot_toggled(self):
        if instances.DiscordBot is None:
            Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        else:
            instances.DiscordBot.stop()

    def _dcbot_server_toggled(self):
        self._active_server.dc_active = int(self.check_boxes["dc_active"].isChecked())

    def _dcbot_full_toggled(self):
        self._active_server.dc_full = int(self.check_boxes["dc_full"].isChecked())

    def _dcbot_id_changed(self, text):
        self._active_server.dc_id = text

    def _serverbutton_clicked(self):
        serveruid = int(self.sender().objectName())
        if serveruid != self._active_server.uid:
            self.buttons[self._active_server.uid].setChecked(False)
            self.load_profile(server_storage.get(serveruid))
        else:
            self.buttons[self._active_server.uid].setChecked(True)

    def _pathbutton_clicked(self):
        new_path = QFileDialog.getExistingDirectory(caption="Select the server folder")
        self._active_server.path = new_path
        self.labels["path"].setText(new_path)
        server_storage.save(self._active_server)

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
        self._active_server.wrapper = instances.Manager.wrapper_module.Wrapper(output=False, args=cmd)
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
