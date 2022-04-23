import os
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
        GUI.MANAGER = manager
        GUI.INSTANCE = self

    MANAGER = None
    INSTANCE = None

    def setup(self):
        self._active_server = self.MANAGER.servers[0]

        self.setWindowTitle("McServerManager")
        self.setStyleSheet("color: #C1C1C1; background-color: #464545;")

        screen = QApplication.primaryScreen()
        self._min_size = QSize(int(screen.size().width() / 4), int(screen.size().height() / 4))
        self.setMinimumSize(self._min_size)

        mainbox = QVBoxLayout()
        widget = QWidget()
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

        for server in self.MANAGER.servers:
            self._buttons[server[0]] = QPushButton(server[0] + "\nstopped")
            self._buttons[server[0]].setObjectName(server[0])
            self._buttons[server[0]].setFixedHeight(50)
            self._buttons[server[0]].clicked.connect(self._button_clicked)
            self._buttons[server[0]].setCheckable(False)
            sideVBox.addWidget(self._buttons[server[0]])

        sideVBox.addStretch()

    def _add_mainarea(self, mainbox):
        mainVBox = QVBoxLayout()
        mainbox.addLayout(mainVBox)

        self._add_overview_area(mainVBox)
        self._add_whitelist_area(mainVBox)
        self._add_startup_area(mainVBox)

        mainVBox.addStretch()

    def _add_overview_area(self, mainVBox):
        overview_groupbox = QGroupBox("Overview")
        overview_groupbox.setCheckable(False)
        mainVBox.addWidget(overview_groupbox)
        overviewVBox = QVBoxLayout()
        overview_groupbox.setLayout(overviewVBox)

        nameHBox = QHBoxLayout()
        self._labels["name"] = QLabel("Server name:")
        self._line_edits["name"] = QLineEdit()
        self._line_edits["name"].textChanged.connect(self._name_changed)
        nameHBox.addWidget(self._labels["name"])
        nameHBox.addWidget(self._line_edits["name"])

        self._buttons["export"] = QPushButton("Export")
        self._buttons["export"].setObjectName("export")
        self._buttons["export"].setFixedWidth(80)
        self._buttons["export"].clicked.connect(lambda *x: print("export button clicked"))
        self._buttons["export"].setCheckable(False)
        nameHBox.addWidget(self._buttons["export"])
        overviewVBox.addLayout(nameHBox)

        pathHBox = QHBoxLayout()
        self._labels["path_label"] = QLabel("Server path:")
        self._labels["path"] = QLabel()
        pathHBox.addWidget(self._labels["path_label"])
        pathHBox.addWidget(self._labels["path"])

        self._buttons["path"] = QPushButton("Set Path")
        self._buttons["path"].setObjectName("path")
        self._buttons["path"].setFixedWidth(80)
        self._buttons["path"].clicked.connect(lambda *x: print("path button clicked"))
        self._buttons["path"].setCheckable(False)
        pathHBox.addWidget(self._buttons["path"])
        overviewVBox.addLayout(pathHBox)

        portHBox = QHBoxLayout()
        self._labels["port"] = QLabel("Port:")
        self._line_edits["port"] = QLineEdit()
        self._line_edits["port"].setPlaceholderText("25565")
        self._line_edits["port"].textChanged.connect(lambda text: config_helper.save_setting(GUI.INSTANCE._active_server[1], "port", text))
        portHBox.addWidget(self._labels["port"])
        portHBox.addWidget(self._line_edits["port"])

        maxplayersHBox = QHBoxLayout()
        self._labels["maxplayers"] = QLabel("Max players:")
        self._line_edits["maxplayers"] = QLineEdit()
        self._line_edits["maxplayers"].setPlaceholderText("20")
        self._line_edits["maxplayers"].textChanged.connect(self._max_players_changed)
        maxplayersHBox.addWidget(self._labels["maxplayers"])
        maxplayersHBox.addWidget(self._line_edits["maxplayers"])

        self._buttons["start"] = QPushButton("Start")
        self._buttons["start"].setObjectName("start")
        self._buttons["start"].setFixedWidth(80)
        self._buttons["start"].clicked.connect(self._start_server)
        self._buttons["start"].setCheckable(False)

        port_maxplayers_HBox = QHBoxLayout()
        port_maxplayers_HBox.addLayout(portHBox)
        port_maxplayers_HBox.addLayout(maxplayersHBox)
        port_maxplayers_HBox.addWidget(self._buttons["start"])
        overviewVBox.addLayout(port_maxplayers_HBox)

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

    def _add_startup_area(self, mainVBox):
        startup_groupbox = QGroupBox("Startup params")
        startup_groupbox.setCheckable(False)
        mainVBox.addWidget(startup_groupbox)
        startupVBox = QVBoxLayout()
        startup_groupbox.setLayout(startupVBox)

        ramHBox = QHBoxLayout()
        self._labels["ram"] = QLabel("RAM:")
        self._line_edits["ram"] = QLineEdit()
        self._line_edits["ram"].setPlaceholderText("4G")
        self._line_edits["ram"].textChanged.connect(self._ram_changed)
        ramHBox.addWidget(self._labels["ram"])
        ramHBox.addWidget(self._line_edits["ram"])

        jarHBox = QHBoxLayout()
        self._labels["jar"] = QLabel("Server jar:")
        self._line_edits["jar"] = QLineEdit()
        self._line_edits["jar"].setPlaceholderText("server.jar")
        self._line_edits["jar"].textChanged.connect(self._jar_changed)
        jarHBox.addWidget(self._labels["jar"])
        jarHBox.addWidget(self._line_edits["jar"])

        javaHBox = QHBoxLayout()
        self._labels["java"] = QLabel("Java executable:")
        self._line_edits["java"] = QLineEdit()
        self._line_edits["java"].setPlaceholderText(os.popen("where java").read().split("\n")[0])
        self._line_edits["java"].textChanged.connect(self._java_changed)
        javaHBox.addWidget(self._labels["java"])
        javaHBox.addWidget(self._line_edits["java"])

        ram_jar_HBox = QHBoxLayout()
        ram_jar_HBox.addLayout(ramHBox)
        ram_jar_HBox.addLayout(jarHBox)
        startupVBox.addLayout(ram_jar_HBox)
        startupVBox.addLayout(javaHBox)

    def _load_config(self):
        self._line_edits["name"].setText(self._active_server[0])
        self._labels["path"].setText(self._active_server[1])

        try:
            self._line_edits["port"].setText(config_helper.get_setting(self._active_server[1], "port"))
        except (KeyError, FileNotFoundError):
            self._line_edits["port"].setText("")

        try:
            self._line_edits["maxplayers"].setText(config_helper.get_setting(self._active_server[1], "maxp"))
        except (KeyError, FileNotFoundError):
            self._line_edits["maxplayers"].setText("")

        try:
            self._line_edits["whitelist"].setText(config_helper.get_setting(self._active_server[1], "whitelist"))
        except (KeyError, FileNotFoundError):
            self._line_edits["whitelist"].setText("")

        try:
            self._line_edits["ram"].setText(config_helper.get_setting(self._active_server[1], "ram"))
        except (KeyError, FileNotFoundError):
            self._line_edits["ram"].setText("")

        try:
            self._line_edits["jar"].setText(config_helper.get_setting(self._active_server[1], "jar"))
        except (KeyError, FileNotFoundError):
            self._line_edits["jar"].setText("")

        try:
            self._line_edits["java"].setText(config_helper.get_setting(self._active_server[1], "java"))
        except (KeyError, FileNotFoundError):
            self._line_edits["java"].setText("")

    def _name_changed(self, text):
        self.MANAGER.change_server_name(self._active_server[0], text)
        self._buttons[text] = self._buttons.pop(self._active_server[0])
        self._buttons[text].setText(text + "\n" + self._buttons[text].text().split("\n")[1])
        self._active_server = [text, self._active_server[1]]

    def _port_changed(self, text):
        config_helper.save_setting(self._active_server[1], "port", text)

    def _max_players_changed(self, text):
        config_helper.save_setting(self._active_server[1], "maxp", text)

    def _whitelist_changed(self, text):
        config_helper.save_setting(self._active_server[1], "whitelist", text)

    def _ram_changed(self, text):
        config_helper.save_setting(self._active_server[1], "ram", text)

    def _jar_changed(self, text):
        config_helper.save_setting(self._active_server[1], "jar", text)

    def _java_changed(self, text):
        config_helper.save_setting(self._active_server[1], "java", text)

    def _button_clicked(self):
        servername = self.sender().objectName()
        server = None
        for item in self.MANAGER.servers:
            if item[0] == servername:
                server = item
        self.load_profile(server[0], server[1])

    def _start_server(self):
        server_name = self._active_server[0]
        self._buttons[server_name].setText(server_name + "\nstarting...")
        config = config_helper.get_settings(self._active_server[1])

        params = ["java", "jar", "ram", "port", "maxp", "whitelist"]
        cmd = self.MANAGER.wrapper_path
        for param in params:
            try:
                cmd += f" -{param} " + config[param] if config[param] != "" else ""
            except KeyError:
                pass

        print(f"Starting {self._active_server[0]} with the following command:")
        print(cmd)
