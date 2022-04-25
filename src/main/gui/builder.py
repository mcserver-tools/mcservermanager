import os
from threading import Thread
from gui.gui import GUI

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout,
                             QWidget)

import core.server_storage as server_storage

def build(manager):
    gui = GUI(manager)

    gui.setWindowTitle("McServerManager")
    gui.setStyleSheet("color: #C1C1C1; background-color: #464545;")

    screen = QApplication.primaryScreen()
    gui._min_size = QSize(int(screen.size().width() / 4), int(screen.size().height() / 4))
    gui.setMinimumSize(gui._min_size)

    mainbox = QVBoxLayout()
    widget = QWidget()
    widget.setLayout(mainbox)
    gui.setCentralWidget(widget)

    _add_header(mainbox)
    contentHBox = QHBoxLayout()
    mainbox.addLayout(contentHBox)
    _add_sidebar(gui, contentHBox)
    _add_mainarea(gui, contentHBox)

    gui.load_profile(server_storage.get(server_storage.keys()[0]))

    gui.buttons[gui._active_server.name].setChecked(True)

    Thread(target=gui._update_players_thread, daemon=True).start()

    return gui

def _add_header(mainbox):
    headerVBox = QVBoxLayout()
    mainbox.addLayout(headerVBox)

    header = QLabel("Minecraft Server Manager")
    headerVBox.addWidget(header)

def _add_sidebar(gui, mainbox):
    sideVBox = QVBoxLayout()
    fixedWidthWidget = QWidget()
    fixedWidthWidget.setFixedWidth(int(gui._min_size.width() / 4))
    fixedWidthWidget.setLayout(sideVBox)
    mainbox.addWidget(fixedWidthWidget)

    for key in server_storage.keys():
        server = server_storage.get(key)
        gui.buttons[server.name] = QPushButton(server.name + "\nstopped")
        gui.buttons[server.name].setObjectName(server.name)
        gui.buttons[server.name].setFixedHeight(50)
        gui.buttons[server.name].clicked.connect(gui._button_clicked)
        gui.buttons[server.name].setCheckable(True)
        sideVBox.addWidget(gui.buttons[server.name])

    sideVBox.addStretch()

def _add_mainarea(gui, mainbox):
    mainVBox = QVBoxLayout()
    mainbox.addLayout(mainVBox)

    _add_overview_area(gui, mainVBox)
    _add_whitelist_area(gui, mainVBox)
    _add_startup_area(gui, mainVBox)

    mainVBox.addStretch()

def _add_overview_area(gui, mainVBox):
    overview_groupbox = QGroupBox("Overview")
    overview_groupbox.setCheckable(False)
    mainVBox.addWidget(overview_groupbox)
    overviewVBox = QVBoxLayout()
    overview_groupbox.setLayout(overviewVBox)

    nameHBox = QHBoxLayout()
    gui.labels["name"] = QLabel("Server name:")
    gui.line_edits["name"] = QLineEdit()
    gui.line_edits["name"].textChanged.connect(gui._name_changed)
    nameHBox.addWidget(gui.labels["name"])
    nameHBox.addWidget(gui.line_edits["name"])

    gui.buttons["export"] = QPushButton("Export")
    gui.buttons["export"].setObjectName("export")
    gui.buttons["export"].setFixedWidth(80)
    gui.buttons["export"].clicked.connect(lambda *x: print("export button clicked"))
    gui.buttons["export"].setCheckable(False)
    nameHBox.addWidget(gui.buttons["export"])
    overviewVBox.addLayout(nameHBox)

    pathHBox = QHBoxLayout()
    gui.labels["path_label"] = QLabel("Server path:")
    gui.labels["path"] = QLabel()
    pathHBox.addWidget(gui.labels["path_label"])
    pathHBox.addWidget(gui.labels["path"])

    gui.buttons["path"] = QPushButton("Set Path")
    gui.buttons["path"].setObjectName("path")
    gui.buttons["path"].setFixedWidth(80)
    gui.buttons["path"].clicked.connect(lambda *x: print("path button clicked"))
    gui.buttons["path"].setCheckable(False)
    pathHBox.addWidget(gui.buttons["path"])
    overviewVBox.addLayout(pathHBox)

    portHBox = QHBoxLayout()
    gui.labels["port"] = QLabel("Port:")
    gui.line_edits["port"] = QLineEdit()
    gui.line_edits["port"].setPlaceholderText("25565")
    gui.line_edits["port"].textChanged.connect(lambda text: server_storage.get(gui._active_server.name).set("port", text))
    portHBox.addWidget(gui.labels["port"])
    portHBox.addWidget(gui.line_edits["port"])

    maxplayersHBox = QHBoxLayout()
    gui.labels["maxplayers"] = QLabel("Max players:")
    gui.line_edits["maxplayers"] = QLineEdit()
    gui.line_edits["maxplayers"].setPlaceholderText("20")
    gui.line_edits["maxplayers"].textChanged.connect(gui._max_players_changed)
    maxplayersHBox.addWidget(gui.labels["maxplayers"])
    maxplayersHBox.addWidget(gui.line_edits["maxplayers"])

    gui.buttons["start"] = QPushButton("Start")
    gui.buttons["start"].setObjectName("start")
    gui.buttons["start"].setFixedWidth(80)
    gui.buttons["start"].clicked.connect(gui._start_button_clicked)
    gui.buttons["start"].setCheckable(False)

    port_maxplayers_HBox = QHBoxLayout()
    port_maxplayers_HBox.addLayout(portHBox)
    port_maxplayers_HBox.addLayout(maxplayersHBox)
    port_maxplayers_HBox.addWidget(gui.buttons["start"])
    overviewVBox.addLayout(port_maxplayers_HBox)

def _add_whitelist_area(gui, mainVBox):
    whitelist_groupbox = QGroupBox("Whitelist")
    whitelist_groupbox.setCheckable(True)
    mainVBox.addWidget(whitelist_groupbox)
    whitelistHBox = QHBoxLayout()
    whitelist_groupbox.setLayout(whitelistHBox)

    gui.labels["whitelist"] = QLabel("Whitelisted players:")
    gui.line_edits["whitelist"] = QLineEdit()
    gui.line_edits["whitelist"].textChanged.connect(gui._whitelist_changed)
    whitelistHBox.addWidget(gui.labels["whitelist"])
    whitelistHBox.addWidget(gui.line_edits["whitelist"])

def _add_startup_area(gui, mainVBox):
    startup_groupbox = QGroupBox("Startup params")
    startup_groupbox.setCheckable(False)
    mainVBox.addWidget(startup_groupbox)
    startupVBox = QVBoxLayout()
    startup_groupbox.setLayout(startupVBox)

    ramHBox = QHBoxLayout()
    gui.labels["ram"] = QLabel("RAM:")
    gui.line_edits["ram"] = QLineEdit()
    gui.line_edits["ram"].setPlaceholderText("4G")
    gui.line_edits["ram"].textChanged.connect(gui._ram_changed)
    ramHBox.addWidget(gui.labels["ram"])
    ramHBox.addWidget(gui.line_edits["ram"])

    jarHBox = QHBoxLayout()
    gui.labels["jar"] = QLabel("Server jar:")
    gui.line_edits["jar"] = QLineEdit()
    gui.line_edits["jar"].setPlaceholderText("server.jar")
    gui.line_edits["jar"].textChanged.connect(gui._jar_changed)
    jarHBox.addWidget(gui.labels["jar"])
    jarHBox.addWidget(gui.line_edits["jar"])

    javaHBox = QHBoxLayout()
    gui.labels["java"] = QLabel("Java executable:")
    gui.line_edits["java"] = QLineEdit()
    gui.line_edits["java"].setPlaceholderText(os.popen("where java").read().split("\n")[0])
    gui.line_edits["java"].textChanged.connect(gui._java_changed)
    javaHBox.addWidget(gui.labels["java"])
    javaHBox.addWidget(gui.line_edits["java"])

    ram_jar_HBox = QHBoxLayout()
    ram_jar_HBox.addLayout(ramHBox)
    ram_jar_HBox.addLayout(jarHBox)
    startupVBox.addLayout(ram_jar_HBox)
    startupVBox.addLayout(javaHBox)
