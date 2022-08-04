"""Module containing the manager class"""

# pylint: disable=E0401, E0611, R0402

import importlib
import logging
import os
import re
import subprocess
import sys
from queue import Queue
from threading import Thread
from time import sleep

import discord_group.discord_bot
import gui.builder as guibuilder
from dataclass.mcserver import McServer
from gui.dialogs import InfoDialog, WarnDialog
from PyQt6.QtWidgets import QApplication

import core.instances as instances
import core.server_storage as server_storage

class Manager():
    """Singleton class containing the main functions"""

    def __init__(self) -> None:
        if instances.MANAGER is not None:
            raise Exception("There is already a manager instance")

        wrapper_path = os.getcwd() + "/src/mcserverwrapper/"
        sys.path.append(wrapper_path)
        spec = importlib.util.spec_from_file_location("wrapper", wrapper_path + "wrapper.py")
        self.wrapper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.wrapper_module)

        instances.MANAGER = self

    def setup(self):
        """Initializes the manager"""

        logging.basicConfig(filename='latest.log', filemode='w', level=logging.WARNING, force=True)

        if not os.path.exists("./servers"):
            logging.info("servers folder doesn't exist, creating...")
            os.mkdir("./servers")

        if instances.DB_MANAGER.get_javaversions() == []:
            logging.info("No saved javaversions have been found, " + \
                         "searching for installed versions...")
            self.save_javaversions(False)

        server_storage.setup()

    def run(self):
        """Creates and starts the gui"""

        app = QApplication([])

        guibuilder.build().show()

        Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        Thread(target=self._check_logs, daemon=True).start()

        app.exec()

    @staticmethod
    def add_server(name, path):
        """Adds a server with given name and path"""

        logging.debug(f"Adding server {name} from {path}")

        uid = instances.DB_MANAGER.get_new_uid()
        server_storage.add(McServer(uid=uid, name=name, path=path))
        instances.GUI.add_server(uid)

    def start_server(self, uid):
        """Starts the server with the given uid"""

        server = server_storage.get(uid)
        cmd, args = server.get_start_command()
        logging.info(f"Starting server {uid} with the following command:\n{cmd}\nwith the following args:\n{args}")

        if instances.GUI.combo_boxes["startup"].currentText() == "bat file":
            cmd = server.batchfile

        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstarting...")

        main_cwd = os.getcwd()
        os.chdir(server.path)
        server.wrapper = instances.MANAGER.wrapper_module.Wrapper(command=cmd, args=args,
                                                                  output=False)
        server_storage.save(server)
        instances.GUI.load_profile_lazy(server.uid)

        try:
            server.wrapper.startup()
        except Exception as exc:
            self.error_occured(exc.args[0])

            server.wrapper = None
            server_storage.save(server)

            os.chdir(main_cwd)
            return

        os.chdir(main_cwd)
        instances.GUI.buttons[server.uid].setText(f"{server.name}\nonline " + \
                                                  f"(0/{server.max_players})")

    @staticmethod
    def stop_server(uid):
        """Stops the server with the given uid"""

        logging.info(f"Stopping server {uid}")

        server = server_storage.get(uid)

        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstopping...")
        if server.wrapper.server_running():
            server.wrapper.stop()
            sleep(5)

        server.wrapper = None
        server_storage.save(server)
        instances.GUI.load_profile_lazy(server.uid)
        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstopped")

    @staticmethod
    def remove_server(uid):
        """Removes the server with the given uid"""

        logging.info(f"Removing server {uid}")

        server_storage.remove(uid)
        instances.GUI.buttons[uid].deleteLater()
        del instances.GUI.buttons[uid]
        instances.GUI.active_server = None
        new_uid = server_storage.uids()[0]
        instances.GUI.load_profile(new_uid)
        instances.GUI.buttons[new_uid].setChecked(True)

    def save_javaversions(self, info_dialog = True):
        """Saves a new javaversion"""

        found_javaversions = self._get_javaversions()
        saved_javaversions = instances.DB_MANAGER.get_javaversions()
        new_versions = [item for item in found_javaversions if item not in saved_javaversions]
        if info_dialog:
            InfoDialog(f"{len(new_versions)} new java installs have been found")
        for item in new_versions:
            instances.DB_MANAGER.add_javaversion(item[0], item[1])

    def error_occured(self, message):
        """Function handling occured errors"""

        if instances.GUI.active_server.wrapper is not None:
            Thread(target=self.stop_server, args=[instances.GUI.active_server.uid,],
                   daemon=True).start()

        logging.error(message)

    def _get_javaversions(self):
        java_versions = []

        if subprocess.run("where java", stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, check=False).returncode == 1:
            WarnDialog("No Java installation found")
            return None

        java_versions.append((f"Java {self._get_version_name('java')}", 'java'))

        drive_letter = subprocess.run("where java", stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL, check=False) \
                                 .stdout.decode("utf-8") \
                                 .split("\n", maxsplit=1)[0][0]
        java_dir = f"{drive_letter}:\\Program Files\\Java"

        version_foldernames = []
        for item in os.listdir(java_dir):
            if not item.startswith("jre"):
                version_foldernames.append(item)

        for item in version_foldernames:
            java_exe_path = f"{java_dir}\\{item}\\bin\\java.exe"
            if os.path.exists(java_exe_path):
                java_version = (f"Java {self._get_version_name(java_exe_path)}", java_exe_path)
                if java_version[0] not in [item[0] for item in java_versions]:
                    java_versions.append(java_version)

        return java_versions

    @staticmethod
    def _get_version_name(path):
        obj = subprocess.run(f'"{path}" --version', stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, check=False)
        if obj.stderr == b'':
            version_output_full = obj.stdout.decode("utf-8")
        else:
            # for older java versions
            obj = subprocess.run(f'"{path}" -version', stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=False)
            version_output_full = obj.stderr.decode("utf-8")

        return re.search(r"[0-9]+\.[0-9]+\.[0-9]+_*[0-9]*\s*", version_output_full).group()

    def _check_logs(self):
        while True:
            for item in server_storage.get_all():
                while item.wrapper is not None and not item.wrapper.output_queue.empty():
                    text = item.wrapper.output_queue.get()
                    if instances.DISCORD_BOT is not None and item.dc_active and item.dc_full \
                       and item.dc_id not in [0, None]:
                        if int(item.dc_id) not in instances.DISCORD_BOT.message_queues:
                            instances.DISCORD_BOT.message_queues[int(item.dc_id)] = Queue()
                        instances.DISCORD_BOT.message_queues[int(item.dc_id)].put(text)
                    if text.startswith("Error:"):
                        self.error_occured(text)
            sleep(0.1)
