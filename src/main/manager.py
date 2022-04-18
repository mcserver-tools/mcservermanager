import os
from PyQt6.QtWidgets import QApplication

from gui import GUI
from mcserver import McServer

class Manager():
    def __init__(self) -> None:
        if self.INSTANCE is None:
            self.servers = []
            self._gui = None
            self.INSTANCE = self

    INSTANCE = None

    def setup(self):
        if not os.path.exists("./servers"):
            os.mkdir("./servers")

    def run(self):
        app = QApplication([])

        self._gui = GUI()
        self._gui.setup()
        self._gui.show()

        app.exec()
