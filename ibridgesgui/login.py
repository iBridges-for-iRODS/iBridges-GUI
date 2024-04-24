"""Pop up Widget for Login."""
import sys
from pathlib import Path

from ibridges import Session
from ibridges.session import LoginError, PasswordError
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi

from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.ui_files.irodsLogin import Ui_irodsLogin


class Login(QDialog, Ui_irodsLogin):
    """Definition and initialization of the iRODS login window."""

    def __init__(self, session_dict):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "irodsLogin.ui", self)

        self.session_dict = session_dict
        self.irods_path = Path('~', '.irods').expanduser()
        self._init_envbox()
        self.cached_pw = self._init_password()
        self._load_gui()
        self.setWindowTitle("Connect to iRODS server")

    def _load_gui(self):
        self.connectButton.clicked.connect(self.login_function)
        self.cancelButton.clicked.connect(self.close)
        self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)

    def _init_envbox(self):
        env_jsons = [
            path.name for path in
            self.irods_path.glob('irods_environment*json')]
        if len(env_jsons) == 0:
            self.envError.setText(f'ERROR: no "irods_environment*json" files found in {self.irods_path}')
        self.envbox.clear()
        self.envbox.addItems(env_jsons)
        self.envbox.setCurrentIndex(0)

    def _init_password(self):
        #Check if there is a cached password
        passwd_file = self.irods_path.joinpath('.irodsA')
        if passwd_file.is_file():
            self.passwordField.setText("***********")
            return True
        return False

    def close(self):
        """Abort login"""
        self.done(0)

    def login_function(self):
        """Connect to iRODS server with gathered info"""
        self.passError.clear()
        env_file = self.irods_path.joinpath(self.envbox.currentText())
        try:
            if self.cached_pw is True and self.passwordField.text() == "***********":
                session = Session(irods_env=env_file)
            else:
                session = Session(irods_env=env_file, password=self.passwordField.text())
            self.session_dict['session'] = session
            session.write_pam_password()
            self.close()
        except LoginError:
            self.passError.setText("irods_environment.json not setup correctly.")
        except PasswordError:
            self.passError.setText("Wrong password!")
        except ConnectionError:
            self.passError.setText("Cannot connect to server. Check Internet, host name and port.")
