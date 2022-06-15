"""Module containing the manager class"""

# pylint: diasble=E0401, E0611

import importlib
import os
import re
import subprocess
import sys
from threading import Thread
from time import sleep

import discord_group.discord_bot
import gui.builder as guibuilder
from dataclass.mcserver import McServer
from PyQt6.QtWidgets import QApplication

import core.instances as instances
import core.server_storage as server_storage
from gui.dialogs import InfoDialog, WarnDialog

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

        if not os.path.exists("./servers"):
            os.mkdir("./servers")

        if instances.DB_MANAGER.get_javaversions() == []:
            self.save_javaversions(False)

        server_storage.setup()

    def run(self):
        """Creates and starts the gui"""

        app = QApplication([])

        guibuilder.build().show()

        Thread(target=discord_group.discord_bot.DiscordBot().start_bot, daemon=True).start()
        Thread(target=self._send_discord_logs, daemon=True).start()

        app.exec()

    def add_server(self, name, path):
        """Adds a server with given name and path"""

        uid = instances.DB_MANAGER.get_new_uid()
        server_storage.add(McServer(uid=uid, name=name, path=path))
        instances.GUI.add_server(uid)

    def start_server(self, uid):
        """Starts the server with the given uid"""

        server = server_storage.get(uid)
        cmd = server.get_start_command()

        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstarting...")

        print(f"Starting {server.name} with the following command:")
        print(cmd[0])

        main_cwd = os.getcwd()
        os.chdir(server.path)
        server.wrapper = instances.MANAGER.wrapper_module.Wrapper(output=False, command=cmd[0], args=cmd[1])
        server_storage.save(server)
        instances.GUI.load_profile_lazy(server.uid)
        server.wrapper.startup()
        os.chdir(main_cwd)

        instances.GUI.buttons[server.uid].setText(f"{server.name}\nonline (0/{server.max_players})")

    def stop_server(self, uid):
        """Stops the server with the given uid"""

        server = server_storage.get(uid)

        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstopping...")
        server.wrapper.stop()
        server.wrapper = None
        server_storage.save(server)
        instances.GUI.load_profile_lazy(server.uid)

        sleep(5)
        instances.GUI.buttons[server.uid].setText(f"{server.name}\nstopped")

    def remove_server(self, uid):
        """Removes the server with the given uid"""

        server_storage.remove(uid)
        instances.GUI.buttons[uid].deleteLater()
        del instances.GUI.buttons[uid]
        instances.GUI._active_server = None
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

    def _get_javaversions(self):
        java_versions = []

        if subprocess.run("where java", stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 1:
            WarnDialog("No Java installation found")
            return

        java_versions.append((f"Java {self._get_version_name('java')}", 'java'))

        drive_letter = subprocess.run("where java", stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL).stdout.decode("utf-8") \
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

    def _get_version_name(self, path):
        obj = subprocess.run(f'"{path}" --version', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if obj.stderr == b'':
            version_output_full = obj.stdout.decode("utf-8")
        else:
            # for older java versions
            obj = subprocess.run(f'"{path}" -version', stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            version_output_full = obj.stderr.decode("utf-8")

        return re.search(r"[0-9]+\.[0-9]+\.[0-9]+_*[0-9]*\s*", version_output_full).group()

    def _send_discord_logs(self):
        while True:
            if instances.DISCORD_BOT is not None:
                for item in server_storage.get_all():
                    if item.wrapper is not None and item.dc_active and item.dc_full \
                       and item.dc_id not in [0, None]:
                        while item.wrapper is not None and not item.wrapper.output_queue.empty():
                            instances.DISCORD_BOT.send(int(item.dc_id),
                                                       item.wrapper.output_queue.get())
            sleep(1)
