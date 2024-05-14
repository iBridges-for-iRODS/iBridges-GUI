"""Pop-up widget definitions."""
import json
import os
import sys

import irods
from ibridges import IrodsPath
from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.uic import loadUi

from ibridgesgui.config import _read_json, check_irods_config, save_irods_config
from ibridgesgui.gui_utils import UI_FILE_DIR, populate_textfield
from ibridgesgui.ui_files.configCheck import Ui_configCheck
from ibridgesgui.ui_files.createCollection import Ui_createCollection


class CreateCollection(QDialog, Ui_createCollection):
    """Popup window to create a new collection."""

    def __init__(self, parent, logger):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "createCollection.ui", self)

        self.logger = logger
        self.setWindowTitle("Create iRODS collection")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.parent = parent
        self.label.setText(str(self.parent) + "/")
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create new collection."""
        if self.collPathLine.text() != "":
            new_coll_path = IrodsPath(self.parent.session, self.parent,
                                    self.collPathLine.text())
            if new_coll_path.exists():
                self.errorLabel.setText(f"{new_coll_path} already exists.")
            else:
                try:
                    IrodsPath.create_collection(new_coll_path.session, new_coll_path)
                    self.logger.info(f"Created collection {new_coll_path}")
                    self.done(0)
                except irods.exception.CAT_NO_ACCESS_PERMISSION:
                    self.errorLabel.setText(f"No access rights to {new_coll_path.parent}."+\
                                            f" Cannot create {self.collPathLine.text()}.")
                except Exception as err:
                    self.logger.exception(f"Could not create {new_coll_path}: {err}")
                    self.errorLabel.setText(f"Could not create {new_coll_path}, consult the logs.")

class CreateDirectory(QDialog, Ui_createCollection):
    """Popup window to create a new directory."""

    def __init__(self, parent):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi("gui/ui_files/createCollection.ui", self)
        self.setWindowTitle("Create directory")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.parent = parent
        self.label.setText(self.parent + os.sep)
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create folder."""
        if self.collPathLine.text() != "":
            new_dir_path = self.parent + os.sep + self.collPathLine.text()
            try:
                os.makedirs(new_dir_path)
                self.done(1)
            except Exception as error:
                if hasattr(error, "message"):
                    self.errorLabel.setText(error.message)
                else:
                    self.errorLabel.setText("ERROR: insufficient rights.")

class CheckConfig(QDialog, Ui_configCheck):
    """Popup window to edit, create and check an environment.json."""

    def __init__(self, logger, env_path):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "configCheck.ui", self)

        self.logger = logger
        self.env_path = env_path
        self.setWindowTitle("Create, edit and inspect iRODS environment")
        self._init_env_box()

        self.envbox.activated.connect(self.load_env)
        self.createButton.clicked.connect(self.create_env)
        self.checkButton.clicked.connect(self.check_env)
        self.saveButton.clicked.connect(self.save_env)
        self.saveasButton.clicked.connect(self.save_env_as)
        self.closeButton.clicked.connect(self.close)


    def _init_env_box(self):
        self.envbox.clear()
        env_jsons = [""]+[
            path.name for path in
            self.env_path.glob("irods_environment*json")]
        if len(env_jsons) != 0:
            self.envbox.addItems(env_jsons)
            self.envbox.setCurrentIndex(0)

    def load_env(self):
        """Load json into text field."""
        self.errorLabel.clear()
        env_file = self.env_path.joinpath(self.envbox.currentText())
        try:
            content = json.dumps(_read_json(env_file),
                                sort_keys=True, indent=4, separators=(",", ": "))
            populate_textfield(self.envEdit, content)
        except IsADirectoryError:
            self.errorLabel.setText("Choose and environment or create a new one.")
        except FileNotFoundError:
            self.errorLabel.setText(f"File does not exist {env_file}")
        except Exception as err:
            self.errorLabel.setText(f"{repr(err)}")

    def create_env(self):
        """Load standard environment into text field."""
        self.errorLabel.clear()
        self.envbox.setCurrentIndex(0)
        env = {
                "irods_host": "<THE SERVER NAME OR IP ADDRESS>",
                "irods_port": 1247,
                "irods_home": "<A DEFAULT LOCATION ON THE IRODS SERVER AS YOUR HOME>",
                "irods_user_name": "<YOUR IRODS USERNAME>",
                "irods_zone_name": "<THE IRODS ZONE NAME>",
                "irods_authentication_scheme": "pam",
                "irods_encryption_algorithm": "AES-256-CBC",
                "irods_encryption_key_size": 32,
                "irods_encryption_num_hash_rounds": 16,
                "irods_encryption_salt_size": 8,
                "irods_client_server_policy": "CS_NEG_REQUIRE",
                "irods_client_server_negotiation": "request_server_negotiation"
              }
        populate_textfield(self.envEdit,
                           json.dumps(env, sort_keys=True, indent=4, separators=(",", ": ")))

    def check_env(self):
        """Check formatting, parameters and connectivity of information in text field."""
        self.errorLabel.clear()
        try:
            msg = check_irods_config(json.loads(self.envEdit.toPlainText()))
        except json.decoder.JSONDecodeError as err:
            msg = "JSON decoding error: "+err.msg
        self.errorLabel.setText(msg)

    def save_env(self):
        """Overwrite file from combobox with information from text field."""
        self.errorLabel.clear()
        env_file = self.env_path.joinpath(self.envbox.currentText())
        if env_file.exists():
            try:
                save_irods_config(env_file, json.loads(self.envEdit.toPlainText()))
                self.errorLabel.setText(f"Configuration saved  as {env_file}")
            except json.decoder.JSONDecodeError:
                self.errorLabel.setText(
                        "Incorrectly formatted. Click 'Check' for more information.")
        else:
            self.errorLabel.setText("Choose 'Save as' to save")

    def save_env_as(self):
        """Choose file to save text field as json."""
        self.errorLabel.clear()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("(*.json)")
        create_file = QFileDialog.getSaveFileName(self, "Save as File",
                                                  str(self.env_path), "(*.json)")
        if create_file[0] != "":
            try:
                save_irods_config(create_file[0], json.loads(self.envEdit.toPlainText()))
                self.errorLabel.setText(f"Configuration saved  as {create_file[0]}")
            except json.decoder.JSONDecodeError:
                self.errorLabel.setText(
                        "Incorrectly formatted. Click 'Check' for more information.")
            except TypeError:
                self.errorLabel.setText("File type needs to be .json")
