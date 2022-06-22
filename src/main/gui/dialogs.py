import logging
import shutil
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QComboBox)

import core.instances as instances

class ConfirmDialog(QDialog):
    def __init__(self, msg, func) -> None:
        super().__init__()

        logging.debug("Creating ConfirmDialog")

        self.func = func

        self.setWindowTitle("Confirm")

        mainBox = QVBoxLayout()
        msg_label = QLabel(msg)
        mainBox.addWidget(msg_label)
        self._add_labels(mainBox)
        self.setLayout(mainBox)
        self.exec()

    def _add_labels(self, mainBox):
        buttonsHBox = QHBoxLayout()

        continue_button = QPushButton("Continue")
        continue_button.setFixedWidth(60)
        continue_button.setCheckable(False)
        continue_button.clicked.connect(self._continue)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(60)
        cancel_button.setCheckable(False)
        cancel_button.clicked.connect(self.deleteLater)

        buttonsHBox.addWidget(continue_button)
        buttonsHBox.addWidget(cancel_button)
        mainBox.addLayout(buttonsHBox)

    def _continue(self):
        self.func()
        self.deleteLater()

class InfoDialog(QDialog):
    def __init__(self, msg) -> None:
        super().__init__()

        logging.debug("Creating InfoDialog")

        self.setWindowTitle("Info")

        mainBox = QVBoxLayout()
        msg_label = QLabel(msg)
        mainBox.addWidget(msg_label)
        self._add_labels(mainBox)
        self.setLayout(mainBox)
        self.exec()

    def _add_labels(self, mainBox):
        ok_button = QPushButton("Ok")
        ok_button.setFixedWidth(60)
        ok_button.setCheckable(False)
        ok_button.clicked.connect(self.deleteLater)

        mainBox.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

class WarnDialog(QDialog):
    def __init__(self, msg) -> None:
        super().__init__()

        logging.debug("Creating WarnDialog")

        self.setWindowTitle("Warning")

        mainBox = QVBoxLayout()
        msg_label = QLabel(msg)
        mainBox.addWidget(msg_label)
        self._add_labels(mainBox)
        self.setLayout(mainBox)
        self.exec()

    def _add_labels(self, mainBox):
        ok_button = QPushButton("Ok")
        ok_button.setFixedWidth(60)
        ok_button.setCheckable(False)
        ok_button.clicked.connect(self.deleteLater)

        mainBox.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

class ErrorDialog(QDialog):
    def __init__(self, msg) -> None:
        super().__init__()

        logging.debug("Creating ErrorDialog")

        self.setWindowTitle("Error")

        mainBox = QVBoxLayout()
        msg_label = QLabel(msg)
        mainBox.addWidget(msg_label)
        self._add_labels(mainBox)
        self.setLayout(mainBox)
        self.exec()

    def _add_labels(self, mainBox):
        ok_button = QPushButton("Ok")
        ok_button.setFixedWidth(60)
        ok_button.setCheckable(False)
        ok_button.clicked.connect(self.deleteLater)

        mainBox.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

class ServerAddDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        logging.debug("Creating ServerAddDialog")

        self.setWindowTitle("Add server")

        self._add_labels()
        self.exec()

    def _add_labels(self):
        buttonsHBox = QHBoxLayout()

        add_button = QPushButton("Add")
        add_button.setFixedWidth(60)
        add_button.setCheckable(False)
        add_button.clicked.connect(self._add_button)

        create_button = QPushButton("Create")
        create_button.setFixedWidth(60)
        create_button.setCheckable(False)
        create_button.clicked.connect(self._create_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(60)
        cancel_button.setCheckable(False)
        cancel_button.clicked.connect(self.deleteLater)

        buttonsHBox.addWidget(add_button)
        buttonsHBox.addWidget(create_button)
        buttonsHBox.addWidget(cancel_button)
        self.setLayout(buttonsHBox)

    def _add_button(self):
        ServerChooseDialog()
        self.deleteLater()

    def _create_button(self):
        ServerChooseDialog()
        self.deleteLater()

class ServerChooseDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        logging.debug("Creating ServerChooseDialogDialog")

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
        path_button.setCheckable(False)
        path_button.clicked.connect(self._browse_directory)
        nameHBox.addWidget(name_label)
        nameHBox.addWidget(self._name)
        nameHBox.addWidget(path_button)
        mainBox.addLayout(nameHBox)

        buttonsHBox = QHBoxLayout()

        send_button = QPushButton("OK")
        send_button.setFixedWidth(60)
        send_button.clicked.connect(self._add_server)
        send_button.setCheckable(False)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(60)
        cancel_button.setCheckable(False)
        cancel_button.clicked.connect(self.deleteLater)

        buttonsHBox.addWidget(send_button)
        buttonsHBox.addWidget(cancel_button)
        mainBox.addLayout(buttonsHBox)

    def _browse_directory(self):
        self._path = QFileDialog.getExistingDirectory(caption="Select the server folder")

    def _add_server(self):
        instances.MANAGER.add_server(self._name.text(), self._path)
        self.deleteLater()

class ServerRemoveDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        logging.debug("Creating ServerRemoveDialog")

        self.setWindowTitle("Remove server")

        self._add_labels()
        self.exec()

    def _add_labels(self):
        buttonsHBox = QHBoxLayout()

        remove_button = QPushButton("Remove")
        remove_button.setFixedWidth(80)
        remove_button.setCheckable(False)
        remove_button.clicked.connect(lambda *x: ConfirmDialog("This will remove the minecraft server, but keep it on your drive. Continue?", self._remove_button))

        rem_del_button = QPushButton("Delete")
        rem_del_button.setFixedWidth(80)
        rem_del_button.setCheckable(False)
        rem_del_button.clicked.connect(lambda *x: ConfirmDialog("This will DELETE the minecraft server from your drive.\nThis is IRREVERSIBLE. Continue?", self._rem_del_button))

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(80)
        cancel_button.setCheckable(False)
        cancel_button.clicked.connect(self.deleteLater)

        buttonsHBox.addWidget(remove_button)
        buttonsHBox.addWidget(rem_del_button)
        buttonsHBox.addWidget(cancel_button)
        self.setLayout(buttonsHBox)

    def _remove_button(self):
        instances.MANAGER.remove_server(instances.GUI.active_server.uid)
        self.deleteLater()

    def _rem_del_button(self):
        path = instances.GUI.active_server.path
        instances.MANAGER.remove_server(instances.GUI.active_server.uid)
        shutil.rmtree(path, ignore_errors=True)
        self.deleteLater()

class JavaOptionsDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        logging.debug("Creating JavaOptionsDialog")

        self._java_combobox = None

        self.setWindowTitle("Java settings")

        self._add_labels()
        self.exec()

    def _add_labels(self):
        mainVBox = QVBoxLayout()

        java_HBox = QHBoxLayout()
        java_label = QLabel("Java Versions:")
        self._java_combobox = QComboBox()

        for item in instances.DB_MANAGER.get_javaversions():
            self._java_combobox.addItem(item[0])

        java_HBox.addWidget(java_label)
        java_HBox.addWidget(self._java_combobox)

        ok_button = QPushButton("Ok")
        ok_button.setFixedWidth(60)
        ok_button.setCheckable(False)
        ok_button.clicked.connect(self.deleteLater)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(80)
        search_button.setCheckable(False)
        search_button.clicked.connect(self._search_button)

        buttonsHBox = QHBoxLayout()
        buttonsHBox.addWidget(ok_button)
        buttonsHBox.addWidget(search_button)

        mainVBox.addLayout(java_HBox)
        mainVBox.addLayout(buttonsHBox)
        self.setLayout(mainVBox)

    def _search_button(self):
        instances.MANAGER.save_javaversions()

        self._java_combobox.clear()
        for item in instances.DB_MANAGER.get_javaversions():
            self._java_combobox.addItem(item[0])

        instances.GUI.combo_boxes["java"].clear()
        for item in instances.DB_MANAGER.get_javaversions():
            instances.GUI.combo_boxes["java"].addItem(item[0])
        java_name = instances.DB_MANAGER.get_javaname(instances.GUI.active_server.javapath)
        index = instances.GUI.combo_boxes["java"].findText(java_name)
        instances.GUI.combo_boxes["java"].setCurrentIndex(index)
