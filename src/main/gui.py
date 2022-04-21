from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QGroupBox

import config_helper

class GUI(QMainWindow):
    def __init__(self, manager):
        super().__init__()

        self._min_size = QSize(0, 0)
        self._buttons = {}
        self._labels = {}
        self._line_edits = {}
        self._active_server = [None, None]
        self.MANAGER = manager

    MANAGER = None

    def setup(self):
        self._active_server = self.MANAGER.servers[0]

        self.setWindowTitle("McServerManager")

        screen = QApplication.primaryScreen()
        self._min_size = QSize(int(screen.size().width() / 4), int(screen.size().height() / 4))
        self.setMinimumSize(self._min_size)

        mainbox = QVBoxLayout()
        widget = QWidget()
        widget.setStyleSheet("color: #C1C1C1; background-color: #464545;")
        widget.setLayout(mainbox)
        self.setCentralWidget(widget)

        # button.clicked.connect(self._button_clicked)
        self._add_header(mainbox)
        contentHBox = QHBoxLayout()
        mainbox.addLayout(contentHBox)
        self._add_sidebar(contentHBox)
        self._add_mainarea(contentHBox)

        self._load_config()

    def load_profile(self, name, path):
        self._active_server = [name, path]
        self._load_config()

    def _add_header(self, mainbox):
        headerVBox = QVBoxLayout()
        mainbox.addLayout(headerVBox)

        header = QLabel("Minecraft Server Manager")
        headerVBox.addWidget(header)

    def _add_sidebar(self, mainbox):
        sideVBox = QVBoxLayout()
        fixedWidthWidget = QWidget()
        fixedWidthWidget.setFixedWidth(int(self._min_size.width() / 4))
        fixedWidthWidget.setLayout(sideVBox)
        mainbox.addWidget(fixedWidthWidget)

        for c, server in enumerate(self.MANAGER.servers):
            self._buttons[server[0]] = QPushButton(f"\n{server[0]}\n")
            self._buttons[server[0]].setObjectName(server[0])
            self._buttons[server[0]].clicked.connect(self._button_clicked)
            self._buttons[server[0]].setCheckable(False)
            sideVBox.addWidget(self._buttons[server[0]])

        sideVBox.addStretch()

    def _add_mainarea(self, mainbox):
        mainVBox = QVBoxLayout()
        mainbox.addLayout(mainVBox)

        self._add_general_area(mainVBox)
        self._add_whitelist_area(mainVBox)

        mainVBox.addStretch()

    def _add_general_area(self, mainVBox):
        general_groupbox = QGroupBox("General")
        # general_groupbox.setStyleSheet("QGroupBox { border: 3px solid white;}")
        general_groupbox.setCheckable(False)
        mainVBox.addWidget(general_groupbox)
        generalVBox = QVBoxLayout()
        general_groupbox.setLayout(generalVBox)

        nameHBox = QHBoxLayout()
        self._labels["name"] = QLabel("Server name:")
        self._line_edits["name"] = QLineEdit()
        self._line_edits["name"].textChanged.connect(self._name_changed)
        nameHBox.addWidget(self._labels["name"])
        nameHBox.addWidget(self._line_edits["name"])
        generalVBox.addLayout(nameHBox)

        portHBox = QHBoxLayout()
        self._labels["port"] = QLabel("Port:")
        self._line_edits["port"] = QLineEdit()
        self._line_edits["port"].setPlaceholderText("25565")
        self._line_edits["port"].textChanged.connect(self._port_changed)
        portHBox.addWidget(self._labels["port"])
        portHBox.addWidget(self._line_edits["port"])

        maxplayersHBox = QHBoxLayout()
        self._labels["maxplayers"] = QLabel("Max players:")
        self._line_edits["maxplayers"] = QLineEdit()
        self._line_edits["maxplayers"].setPlaceholderText("20")
        self._line_edits["maxplayers"].textChanged.connect(self._max_players_changed)
        maxplayersHBox.addWidget(self._labels["maxplayers"])
        maxplayersHBox.addWidget(self._line_edits["maxplayers"])

        port_maxplayers_HBox = QHBoxLayout()
        port_maxplayers_HBox.addLayout(portHBox)
        port_maxplayers_HBox.addLayout(maxplayersHBox)
        generalVBox.addLayout(port_maxplayers_HBox)

    def _add_whitelist_area(self, mainVBox):
        whitelist_groupbox = QGroupBox("Whitelist")
        whitelist_groupbox.setCheckable(True)
        mainVBox.addWidget(whitelist_groupbox)
        whitelistHBox = QHBoxLayout()
        whitelist_groupbox.setLayout(whitelistHBox)

        self._labels["whitelist"] = QLabel("Whitelisted players:")
        self._line_edits["whitelist"] = QLineEdit()
        self._line_edits["whitelist"].textChanged.connect(self._whitelist_changed)
        whitelistHBox.addWidget(self._labels["whitelist"])
        whitelistHBox.addWidget(self._line_edits["whitelist"])

    def _load_config(self):
        try:
            self._line_edits["name"].setText(self._active_server[0])
            self._line_edits["port"].setText(config_helper.get_setting(self._active_server[1], "port"))
            self._line_edits["maxplayers"].setText(config_helper.get_setting(self._active_server[1], "maxp"))
            self._line_edits["whitelist"].setText(config_helper.get_setting(self._active_server[1], "whitelist"))
        except KeyError:
            pass
        except FileNotFoundError:
            pass

    def _name_changed(self, text):
        self.MANAGER.change_server_name(self._active_server[0], text)
        self._buttons[text] = self._buttons.pop(self._active_server[0])
        self._buttons[text].setText("\n" + text + "\n")
        self._active_server = [text, self._active_server[1]]

    def _port_changed(self, text):
        config_helper.save_setting(self._active_server[1], "port", text)

    def _max_players_changed(self, text):
        config_helper.save_setting(self._active_server[1], "maxp", text)

    def _whitelist_changed(self, text):
        config_helper.save_setting(self._active_server[1], "whitelist", text)

    def _button_clicked(self):
        servername = self.sender().objectName()
        server = None
        for item in self.MANAGER.servers:
            if item[0] == servername:
                server = item
        self.load_profile(server[0], server[1])
