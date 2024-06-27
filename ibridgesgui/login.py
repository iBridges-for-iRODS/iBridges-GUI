"""Pop up Widget for Login."""

import logging
import sys
from pathlib import Path

from ibridges import IrodsPath, Session
from ibridges.resources import Resources
from ibridges.session import LoginError, PasswordError
from irods.exception import ResourceDoesNotExist
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi

from ibridgesgui.config import get_last_ienv_path, set_last_ienv_path
from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.ui_files.irodsLogin import Ui_irodsLogin


class Login(QDialog, Ui_irodsLogin):
    """Definition and initialization of the iRODS login window."""

    def __init__(self, session_dict, app_name):
        """Initialise tab."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            loadUi(UI_FILE_DIR / "irodsLogin.ui", self)

        self.logger = logging.getLogger(app_name)
        self.irods_config_dir = Path("~", ".irods").expanduser()

        self.session_dict = session_dict
        self._init_envbox()
        self.cached_pw = self._init_password()
        self._load_gui()
        self.setWindowTitle("Connect to iRODS server")

    def _load_gui(self):
        self.connect_button.clicked.connect(self.login_function)
        self.cancel_button.clicked.connect(self.close)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)

    def _init_envbox(self):
        env_jsons = [path.name for path in self.irods_config_dir.glob("irods_environment*json")]
        if len(env_jsons) == 0:
            self.envError.setText(
                f"ERROR: no irods_environment*json files found in {self.irods_config_dir}"
            )

        self.envbox.clear()
        self.envbox.addItems(env_jsons)
        last_env = get_last_ienv_path()
        if last_env is not None and last_env in env_jsons:
            self.envbox.setCurrentIndex(env_jsons.index(last_env))
        else:
            self.envbox.setCurrentIndex(0)

    def _init_password(self):
        # Check if there is a cached password
        passwd_file = self.irods_config_dir.joinpath(".irodsA")
        if passwd_file.is_file():
            self.password_field.setText("***********")
            return True
        return False

    def close(self):
        """Abort login."""
        self.done(0)

    def _check_home(self, session):
        if not IrodsPath(session).collection_exists():
            return False
        return True

    def _check_resource(self, session):
        resc = Resources(session).get_resource(session.default_resc)
        if resc.parent is not None:
            return False
        return True

    def login_function(self):
        """Connect to iRODS server with gathered info."""
        self.error_label.clear()
        env_file = self.irods_config_dir.joinpath(self.envbox.currentText())
        try:
            if self.cached_pw is True and self.password_field.text() == "***********":
                self.logger.debug("Login with %s and cached password.", env_file)
                session = Session(irods_env=env_file)
            else:
                session = Session(irods_env=env_file, password=self.password_field.text())
                self.logger.debug("Login with %s and password from prompt.", env_file)
            self.logger.info(
                "Logged in as %s to %s; working coll %s",
                session.username,
                session.host,
                session.home,
            )
            session.write_pam_password()
            if self._check_home(session) and self._check_resource(session):
                self.session_dict["session"] = session
                set_last_ienv_path(env_file.name)
                self.close()
            elif not self._check_home(session):
                self.error_label.setText(f'"irods_home": "{session.home}" does not exist.')
            elif not self._check_resource(session):
                self.error_label.setText(
                    f'"irods_default_resource": "{session.default_resc}" not writeable.'
                )

        except LoginError:
            self.error_label.setText("irods_environment.json not setup correctly.")
            self.logger.error("irods_environment.json not setup correctly.")
        except PasswordError:
            self.error_label.setText("Wrong password!")
            self.logger.error("Wrong password provided.")
        except ConnectionError:
            self.error_label.setText(
                "Cannot connect to server. Check Internet, host name and port."
            )
            self.logger.exception("Network error.")
        except ResourceDoesNotExist:
            self.error_label.setText('"irods_default_resource" does not exist.')
            self.logger.exception("Default resource does not exist.")
        except Exception as err:
            log_path = Path("~/.ibridges")
            self.logger.exception("Failed to login: %s", repr(err))
            self.error_label.setText(f"Login failed, consult the log file(s) in {log_path}")
