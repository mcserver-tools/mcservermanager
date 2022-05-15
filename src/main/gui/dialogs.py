from PyQt6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout)

import core.instances as instances

class ServerAddDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self._name = None
        self._path = None

        self.setWindowTitle("Add server")

        mainBox = QVBoxLayout()
        self.setLayout(mainBox)
        self._add_labels(mainBox)
        self.exec()

    def _add_labels(self, mainBox: QVBoxLayout):
        nameHBox = QHBoxLayout()
        name_label = QLabel("Server name:")
        self._name = QLineEdit()
        path_button = QPushButton("Browse")
        path_button.setFixedWidth(80)
        path_button.clicked.connect(self._browse_directory)
        path_button.setCheckable(False)
        nameHBox.addWidget(name_label)
        nameHBox.addWidget(self._name)
        nameHBox.addWidget(path_button)
        mainBox.addLayout(nameHBox)

        send_button = QPushButton("OK")
        send_button.setFixedWidth(60)
        send_button.clicked.connect(self._add_server)
        send_button.setCheckable(False)
        mainBox.addWidget(send_button)

    def _browse_directory(self):
        self._path = QFileDialog.getExistingDirectory(caption="Select the server folder")

    def _add_server(self):
        instances.Manager.add_server(self._name.text(), self._path)
        self.deleteLater()
