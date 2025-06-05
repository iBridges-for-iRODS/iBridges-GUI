"""Pop up Widget for Login."""

import logging
import os
import sys
from pathlib import Path

from ibridges import IrodsPath, Session
from ibridges.resources import Resources
from ibridges.session import LoginError, PasswordError
from irods.exception import ResourceDoesNotExist
from PySide6.QtWidgets import QDialog, QLineEdit

from ibridgesgui.config import (
    IRODSA,
    check_irods_config,
    combine_envs_gui_cli,
    get_last_ienv_name,
    get_prev_settings,
    save_current_settings,
    set_last_ienv,
)
from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.irodsLogin import Ui_irodsLogin


def strictwrite(path, flags, mode=0o600):
    """Create opener for the standard open command to modify the umask."""
    return os.open(path, flags, mode)


class Login(QDialog, Ui_irodsLogin):
    """Definition and initialization of the iRODS login window."""

    def __init__(self, session_dict, app_name):
        """Initialise tab."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "irodsLogin.ui", self)

        self.logger = logging.getLogger(app_name)
        self.irods_config_dir = Path("~", ".irods").expanduser()

        self.session_dict = session_dict
        # get settings from GUI and CLI form previous sessions
        self.aliases_envs = combine_envs_gui_cli()
        self._init_envbox()
        self.prev_settings = get_prev_settings()  # previous env file or alias
        self._load_gui()
        self.setWindowTitle("Connect to iRODS server")

    def _load_gui(self):
        self.connect_button.clicked.connect(self.login_function)
        self.cancel_button.clicked.connect(self.close)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.envbox.currentTextChanged.connect(self._init_password)

    def _init_envbox(self):
        # all env files in the .irods folder
        env_files = list(self.irods_config_dir.glob('*.json'))
        if len(env_files) == 0:
            self.error_label.setText(f"ERROR: no .json files found in {self.irods_config_dir}")

        # find env files which are not aliased
        aliased_envs = [Path(env) for env, _ in self.aliases_envs.values()]
        env_files = [x for x in env_files if x not in aliased_envs]

        # add remaining items to dictionary
        for env_file in env_files:
            self.aliases_envs[env_file.name] = (env_file, None)

        # Drop down for aliases should also show env file path
        envbox_items = [
            key + " - " + str(Path(value[0])) for key, value in self.aliases_envs.items()
        ]

        self.envbox.clear()
        self.envbox.addItems(envbox_items)
        last_env = get_last_ienv_name()
        if last_env is not None and last_env in envbox_items:
            self.envbox.setCurrentIndex(envbox_items.index(last_env))
        else:
            self.envbox.setCurrentIndex(0)
        self._init_password()

    def _init_password(self):
        # Check if there is a cached password in the ibridges_gui config file
        env_or_alias = self.envbox.currentText().split(" - ")[0]
        if env_or_alias in self.aliases_envs and self.aliases_envs[env_or_alias][1]:
            self.password_field.setText("***********")
            return True
        self.password_field.clear()
        return False

    def close(self):
        """Abort login."""
        self.done(0)

    def _check_home(self, session):
        if not IrodsPath(session).collection_exists():
            return False
        return True

    def _check_resource(self, session):
        try:
            resc = Resources(session).get_resource(session.default_resc)
            if resc.parent is not None:
                return False
            return True
        except Exception:
            return False

    def login_function(self):
        """Connect to iRODS server with gathered info."""
        self.error_label.clear()
        selected_env = self.envbox.currentText()
        env_file, cached_pw = self.aliases_envs[selected_env.split(" - ")[0]]

        msg = check_irods_config(Path(env_file), include_network=False)
        if not msg == "All checks passed successfully.":
            self.error_label.setText("Go to menu Configure. \n" + msg)
            return

        try:
            if cached_pw and self.password_field.text() == "***********":
                self.logger.debug("Login with %s and cached password.", env_file)
                with open(IRODSA, "w", encoding="utf-8", opener=strictwrite) as f:
                    f.write(cached_pw)

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
            save_current_settings(env_file)
            if self._check_home(session) and self._check_resource(session):
                self.session_dict["session"] = session
                set_last_ienv(selected_env)
                self.close()
            elif not self._check_home(session):
                self.error_label.setText(f'"irods_home": "{session.home}" does not exist.')
                return
            elif not self._check_resource(session):
                self.error_label.setText(
                    f'"irods_default_resource": "{session.default_resc}" not writeable.'
                )
                return

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
