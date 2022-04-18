from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QGroupBox

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self._min_size = QSize(0, 0)
        self._buttons = {}
        self._labels = {}
        self._line_edits = {}

    def setup(self):
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

        self._buttons["server1"] = QPushButton("\nServer1\n")
        self._buttons["server1"].setCheckable(False)
        sideVBox.addWidget(self._buttons["server1"])

        self._buttons["server3"] = QPushButton("\nServer3\n")
        self._buttons["server3"].setCheckable(False)
        sideVBox.addWidget(self._buttons["server3"])

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
        nameHBox.addWidget(self._labels["name"])
        nameHBox.addWidget(self._line_edits["name"])
        generalVBox.addLayout(nameHBox)

        portHBox = QHBoxLayout()
        self._labels["port"] = QLabel("Port:")
        self._line_edits["port"] = QLineEdit()
        portHBox.addWidget(self._labels["port"])
        portHBox.addWidget(self._line_edits["port"])

        maxplayersHBox = QHBoxLayout()
        self._labels["maxplayers"] = QLabel("Max players:")
        self._line_edits["maxplayers"] = QLineEdit()
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
        whitelistHBox.addWidget(self._labels["whitelist"])
        whitelistHBox.addWidget(self._line_edits["whitelist"])

    def _button_clicked(self):
        print(f"Clicked")

    def _button_released(self):
        print(f"Released")
