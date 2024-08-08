"""Popup widgets for upload, download, create dir/coll, rename, check config."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import irods
from ibridges import IrodsPath, download, upload
from ibridges.util import find_environment_provider, get_environment_providers
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.uic import loadUi

from ibridgesgui.config import _read_json, check_irods_config, get_last_ienv_path, save_irods_config
from ibridgesgui.gui_utils import UI_FILE_DIR, combine_operations, populate_textfield
from ibridgesgui.threads import TransferDataThread
from ibridgesgui.ui_files.configCheck import Ui_configCheck
from ibridgesgui.ui_files.createCollection import Ui_createCollection
from ibridgesgui.ui_files.downloadData import Ui_downloadData
from ibridgesgui.ui_files.renameItem import Ui_renameItem
from ibridgesgui.ui_files.uploadData import Ui_uploadData


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
        if self.coll_path_input.text() != "":
            new_coll_path = IrodsPath(self.parent.session, self.parent, self.coll_path_input.text())
            if new_coll_path.exists():
                self.error_label.setText(f"{new_coll_path} already exists.")
            else:
                try:
                    IrodsPath.create_collection(new_coll_path.session, new_coll_path)
                    self.logger.info(f"Created collection {new_coll_path}")
                    self.done(0)
                except irods.exception.CAT_NO_ACCESS_PERMISSION:
                    self.error_label.setText(
                        f"No access rights to {new_coll_path.parent}."
                        + f" Cannot create {self.coll_path_input.text()}."
                    )
                except Exception as err:
                    self.logger.exception(f"Could not create {new_coll_path}: {err}")
                    self.error_label.setText(f"Could not create {new_coll_path}, consult the logs.")


class CreateDirectory(QDialog, Ui_createCollection):
    """Popup window to create a new directory."""

    def __init__(self, parent):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "createCollection.ui", self)
        self.setWindowTitle("Create Directory")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.parent = parent
        self.label.setText(self.parent + os.sep)
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create folder."""
        if self.coll_path_input.text() != "":
            new_dir_path = self.parent + os.sep + self.coll_path_input.text()
            try:
                os.makedirs(new_dir_path)
                self.done(1)
            except FileExistsError:
                self.error_label.setText("ERROR: Folder already exists.")
            except Exception as error:
                if hasattr(error, "message"):
                    self.error_label.setText(error.message)
                else:
                    self.error_label.setText("ERROR: insufficient rights.")


class Rename(QDialog, Ui_renameItem):
    """Popup window to rename and move a collection or data object."""

    def __init__(self, irods_path: IrodsPath, logger):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "renameItem.ui", self)

        self.logger = logger
        self.setWindowTitle("Create iRODS collection")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.irods_path = irods_path
        self.item_path_label.setText(str(irods_path))
        self.item_path_input.setText(str(irods_path))
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create new collection."""
        if self.item_path_input.text() != "":
            new_path = IrodsPath(self.irods_path.session, self.item_path_input.text())
            if new_path.exists():
                self.error_label.setText(f"{new_path} already exists.")
            else:
                try:
                    new_irods_path = self.irods_path.rename(new_path)
                    self.logger.info(f"Rename/Move {self.irods_path} --> {new_irods_path}")
                    self.done(0)
                except irods.exception.CAT_NO_ACCESS_PERMISSION:
                    self.error_label.setText(f"No access rights to {new_path}.")
                except Exception as err:
                    self.logger.exception(f"Could not create {new_path}: {err}")
                    self.error_label.setText(f"Could not create {new_path}, consult the logs.")


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

        providers = get_environment_providers()
        self.templates = {
            f"Template - {key} ({descr})": key
            for p in providers
            for key, descr in p.descriptions.items()
        }
        self._init_env_box()

        self.envbox.activated.connect(self.load)
        self.new_button.clicked.connect(self.create_env)
        self.check_button.clicked.connect(self.check_env)
        self.save_button.clicked.connect(self.save_env)
        self.save_as_button.clicked.connect(self.save_env_as)
        self.close_button.clicked.connect(self.close)

    def _init_env_box(self):
        self.envbox.clear()
        env_jsons = [""] + [path.name for path in self.env_path.glob("irods_environment*json")]
        if len(env_jsons) != 0:
            self.envbox.addItems(env_jsons)
        self.envbox.addItems(self.templates.keys())
        self.envbox.setCurrentIndex(0)

    def load(self):
        """Decide whether load template or irods env."""
        selected = self.envbox.currentText()
        if selected.startswith("Template - "):
            self.load_template(self.templates[selected])
        else:
            self.load_env(self.env_path.joinpath(selected))

    def load_template(self, template_key):
        """Load environment template into text field."""
        self.error_label.clear()
        provider = find_environment_provider(get_environment_providers(), template_key)
        env_json = provider.environment_json(
            template_key, *[q.upper() for q in provider.questions]
        ).split("\n")
        populate_textfield(self.env_field, env_json)
        self.error_label.setText("Please fill in your user name.")

    def load_env(self, env_file):
        """Load json into text field."""
        self.error_label.clear()
        try:
            content = json.dumps(
                _read_json(env_file), sort_keys=True, indent=4, separators=(",", ": ")
            )
            populate_textfield(self.env_field, content)
        except IsADirectoryError:
            self.error_label.setText("Choose and environment or create a new one.")
        except FileNotFoundError:
            self.error_label.setText(f"File does not exist {env_file}")
        except Exception as err:
            self.error_label.setText(f"{repr(err)}")

    def create_env(self):
        """Load standard environment into text field."""
        self.error_label.clear()
        self.envbox.setCurrentIndex(0)
        env = {
            "irods_host": "<THE SERVER NAME OR IP ADDRESS>",
            "irods_port": 1247,
            "irods_home": "<A DEFAULT LOCATION ON THE IRODS SERVER AS YOUR HOME>",
            "irods_default_resource": "<A DEFAULT IRODS RESOURCE NAME>",
            "irods_user_name": "<YOUR IRODS USERNAME>",
            "irods_zone_name": "<THE IRODS ZONE NAME>",
            "irods_authentication_scheme": "pam",
            "irods_encryption_algorithm": "AES-256-CBC",
            "irods_encryption_key_size": 32,
            "irods_encryption_num_hash_rounds": 16,
            "irods_encryption_salt_size": 8,
            "irods_client_server_policy": "CS_NEG_REQUIRE",
            "irods_client_server_negotiation": "request_server_negotiation",
        }
        populate_textfield(
            self.env_field, json.dumps(env, sort_keys=True, indent=4, separators=(",", ": "))
        )

    def check_env(self):
        """Check formatting, parameters and connectivity of information in text field."""
        self.error_label.clear()
        try:
            msg = check_irods_config(json.loads(self.env_field.toPlainText()))
        except json.decoder.JSONDecodeError as err:
            msg = f"JSON decoding error: {err.msg} at position {err.pos}."
        self.error_label.setText(msg)

    def save_env(self):
        """Overwrite file from combobox with information from text field."""
        self.error_label.clear()
        env_file = self.env_path.joinpath(self.envbox.currentText())
        if env_file.is_file():
            try:
                save_irods_config(env_file, json.loads(self.env_field.toPlainText()))
                self.error_label.setText(f"Configuration saved  as {env_file}")
            except json.decoder.JSONDecodeError:
                self.error_label.setText(
                    "Incorrectly formatted. Click 'Check' for more information."
                )
        else:
            self.error_label.setText("Choose 'Save as' to save")

    def save_env_as(self):
        """Choose file to save text field as json."""
        self.error_label.clear()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("(*.json)")
        create_file = QFileDialog.getSaveFileName(
            self, "Save as File", str(self.env_path), "(*.json)"
        )
        if create_file[0] != "":
            try:
                save_irods_config(create_file[0], json.loads(self.env_field.toPlainText()))
                self.error_label.setText(f"Configuration saved  as {create_file[0]}")
            except json.decoder.JSONDecodeError:
                self.error_label.setText(
                    "Incorrectly formatted. Click 'Check' for more information."
                )
            except TypeError:
                self.error_label.setText("File type needs to be .json")


class UploadData(QDialog, Ui_uploadData):
    """Popup window to upload data to browser."""

    def __init__(self, logger, session, irods_path):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "uploadData.ui", self)

        self.active_upload = False
        self.upload_thread = None
        self.selected_data = []
        self.logger = logger
        self.session = session
        self.irods_path = irods_path

        self.destination_label.setText(str(irods_path))

        self.upload_button.clicked.connect(self._get_upload_params)
        self.file_button.clicked.connect(self.select_file)
        self.folder_button.clicked.connect(self.select_folder)
        self.hide_button.clicked.connect(self.close_window)

    def close_window(self):
        """Close window while data transfer stays in progress."""
        if self.active_upload:
            reply = QMessageBox.critical(
                self,
                "Message",
                "Do you want to close the window while the transfer continues?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.active_upload = False
        self.close()

    # pylint: disable=C0103
    def closeEvent(self, evnt):  # noqa
        """Override close when download is in process."""
        if self.active_upload:
            evnt.ignore()

    def select_file(self):
        """Open file selector."""
        select_file = QFileDialog.getOpenFileName(self, "Open Filie")
        path = self._fs_select(select_file)
        if path is None or str(path) == "." or path in self.sources_list.toPlainText():
            return
        self.sources_list.append(path)

    def select_folder(self):
        """Open folder selctor."""
        select_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        path = self._fs_select(select_dir)
        if path is None or str(path) == "." or path in self.sources_list.toPlainText():
            return
        self.sources_list.append(path)

    def _get_upload_params(self):
        local_paths = [Path(lp) for lp in self.sources_list.toPlainText().split("\n") if lp != ""]

        if len(local_paths) == 0:
            self.error_label.setText("Please select a file or folder to upload.")
            return

        self._start_upload(local_paths)

    def _start_upload(self, lpaths):
        self._enable_buttons(False)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.active_upload = True
        self.error_label.setText(f"Uploading to {str(self.irods_path)} ....")
        env_path = Path("~").expanduser().joinpath(".irods", get_last_ienv_path())

        try:
            ops = combine_operations(
                [
                    upload(
                        self.session,
                        p,
                        self.irods_path,
                        overwrite=self.overwrite.isChecked(),
                        dry_run=True,
                    )
                    for p in lpaths
                ]
            )

            self.upload_thread = TransferDataThread(
                env_path, self.logger, ops, overwrite=self.overwrite.isChecked()
            )

        except FileExistsError:
            self.error_label.setText("Data already exists. Check 'overwrite' to overwrite.")
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            self._enable_buttons(True)
            return
        except Exception as err:
            self.error_label.setText(
                f"Could not instantiate a new session from {env_path}: {repr(err)}."
            )
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            self._enable_buttons(True)
            return

        self.upload_thread.succeeded.connect(self._upload_end)
        self.upload_thread.finished.connect(self._finish_upload)
        self.upload_thread.current_progress.connect(self._upload_status)
        self.upload_thread.start()

    def _finish_upload(self):
        #self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        del self.upload_thread

    def _upload_status(self, state):
        up_size, transferred_size, obj_count, num_objs, obj_failed = state
        self.progress_bar.setValue(int(transferred_size*100/up_size))
        text = f"{obj_count} of {num_objs} files; failed: {obj_failed}."
        self.error_label.setText(text)

    def _upload_end(self, thread_output: dict):
        self.active_upload = False
        if thread_output["error"] == "":
            self.error_label.setText("Upload finished.")
        else:
            self.error_label.setText("Errors occurred during upload. Consult the logs.")
        #self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def _enable_buttons(self, enable):
        self.upload_button.setEnabled(enable)
        self.folder_button.setEnabled(enable)
        self.file_button.setEnabled(enable)
        self.overwrite.setEnabled(enable)

    def _fs_select(self, path_select):
        """Retrieve the path (file or folder) from a QFileDialog."""
        if isinstance(path_select, tuple):
            path = path_select[0]
        else:
            path = path_select

        return path


class DownloadData(QDialog, Ui_downloadData):
    """Popup window to dowload data from browser."""

    def __init__(self, logger, session, irods_path):
        """Initialise window."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "downloadData.ui", self)

        self.active_download = False
        self.download_thread = None
        self.logger = logger
        self.session = session
        self.irods_path = irods_path

        self.source_browser.append(self.irods_path_tree())
        self.timestamp = datetime.now().strftime("%m%d%Y-%H%M")
        self.meta_path = None
        self.meta_download = (
            f"bridges_metadata_{self.irods_path.name.split('.')[0]}_{self.timestamp}.json"
        )
        self.metadata.setText(f"Store metadata as\n{self.meta_download}")
        self.folder_button.clicked.connect(self.select_folder)
        self.download_button.clicked.connect(self._get_download_params)
        self.hide_button.clicked.connect(self.close_window)

    def close_window(self):
        """Close window while data transfer stays in progress."""
        if self.active_download:
            reply = QMessageBox.critical(
                self,
                "Message",
                "Do you want to close the window while the transfer continues?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.active_download = False
        self.close()

    # pylint: disable=C0103
    def closeEvent(self, evnt):  # noqa
        """Override close when download is in process."""
        if self.active_download:
            evnt.ignore()

    def irods_path_tree(self):
        """Expand the irods_path if it is a collection."""
        if self.irods_path.collection_exists():
            return "\n".join(
                [coll.name for coll in self.irods_path.collection.subcollections]
                + [obj.name for obj in self.irods_path.collection.data_objects]
            )

        return str(self.irods_path)

    def select_folder(self):
        """Select the download destination."""
        select_dir = Path(
            QFileDialog.getExistingDirectory(
                self, "Select Directory", directory=str(Path("~").expanduser())
            )
        )
        if str(select_dir) == "" or str(select_dir) == ".":
            return
        self.destination_label.setText(str(select_dir))

    def _get_download_params(self):
        """Retrieve and check all parameters for the dpwnload."""
        local_path = Path(self.destination_label.text())
        if local_path is None or str(local_path) == ".":
            self.error_label.setText("Select a download folder.")
            return

        if not local_path.is_dir():
            self.error_label.setText(
                f"Dowload folder {local_path} dows not exist or is not a folder."
            )
            return

        if self.metadata.isChecked():
            self.meta_path = local_path.joinpath(self.meta_download)

        self._start_download(local_path)

    def _enable_buttons(self, enable):
        self.download_button.setEnabled(enable)
        self.folder_button.setEnabled(enable)
        self.overwrite.setEnabled(enable)
        self.metadata.setEnabled(enable)

    def _start_download(self, local_path):
        self.active_download = True
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self._enable_buttons(False)
        self.error_label.setText(f"Downloading to {local_path} ....")
        env_path = Path("~").expanduser().joinpath(".irods", get_last_ienv_path())
        try:
            ops = download(
                self.session,
                self.irods_path,
                local_path,
                overwrite=self.overwrite.isChecked(),
                metadata=self.meta_path,
                dry_run=True,
            )
            self.download_thread = TransferDataThread(
                env_path, self.logger, ops, overwrite=self.overwrite.isChecked()
            )
        except FileExistsError:
            self.error_label.setText("Data already exists. Check 'overwrite' to overwrite.")
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            self._enable_buttons(True)
            return
        except Exception as err:
            self.error_label.setText(
                f"Could not instantiate a new session from {env_path}: {repr(err)}."
            )
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            self._enable_buttons(True)
            return

        self.download_thread.succeeded.connect(self._download_end)
        self.download_thread.finished.connect(self._finish_download)
        self.download_thread.current_progress.connect(self._download_status)
        self.download_thread.start()

    def _finish_download(self):
        #self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        del self.download_thread

    def _download_status(self, state):
        down_size, transferred_size, obj_count, num_objs, obj_failed = state
        self.progress_bar.setValue(int(transferred_size*100/down_size))
        text = f"{obj_count} of {num_objs} files; failed: {obj_failed}."
        self.error_label.setText(text)

    def _download_end(self, thread_output: dict):
        self.active_download = False
        if thread_output["error"] == "":
            self.error_label.setText("Download finished.")
        else:
            self.error_label.setText("Errors occurred during download. Consult the logs.")
        #self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
