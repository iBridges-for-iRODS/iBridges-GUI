"""Login widget."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ibridges import Session
from ibridges.session import LoginError, PasswordError
from irods.exception import ResourceDoesNotExist
from PySide6.QtWidgets import QDialog, QLineEdit

from ibridgesgui.config import (
    IRODSA,
    check_irods_config,
    get_last_ienv_name,
    load_envs_from_cli_and_fs,
)
from ibridgesgui.ui_files.irodsLogin import Ui_irodsLogin


class LoginDialog(QDialog, Ui_irodsLogin):
    """Login dialog that loads an iRODS environment file and collects password."""

    def __init__(self, parent=None, logger=None, session_manager=None) -> None:
        """Init."""
        super().__init__(parent)
        self.setupUi(self)
        self.logger = logger
        self.session_manager = session_manager
        self.irods_config_dir = Path("~", ".irods").expanduser()

        self.aliases_envs = load_envs_from_cli_and_fs(self.irods_config_dir)
        self.accepted_credentials: dict[str, Any] | None = None
        self.password_field.setEchoMode(QLineEdit.Password)
        self.error_label.setWordWrap(True)

        # Connect buttons
        self.connect_button.clicked.connect(self._on_connect)
        self.cancel_button.clicked.connect(self.reject)
        self.envbox.currentIndexChanged.connect(lambda _: self._init_password())


        # Populate environment file dropdown
        self._init_envbox()

    def _init_envbox(self):
        items = [f"{alias} - {path}" for alias, (path, _) in self.aliases_envs.items()]

        last = get_last_ienv_name()
        if last:
            for item in items:
                if item.startswith(f"{last} - "):
                    items.remove(item)
                    items.insert(0, item)
                    break

        self.envbox.clear()
        self.envbox.addItems(items)


    def _init_password(self):
        parsed = self._parse_envbox_text()
        if parsed is None:
            self.password_field.clear()
            return False

        _, env_path = parsed
        env_path = env_path.expanduser().resolve()

        entry = None
        for _, (p, e) in self.aliases_envs.items():
            if Path(p).expanduser().resolve() == env_path:
                entry = e
                break

        if entry is None:
            self.password_field.clear()
            return False

        cached_pw = entry.get("irodsa_backup")
        if cached_pw:
            self.password_field.setText("***********")
            return True

        self.password_field.clear()
        return False

    def _get_env_selection(self):
        parsed = self._parse_envbox_text()
        if parsed is None:
            self.error_label.setText("No environment selected.")
            return None
        alias, env_path = parsed
        return alias, env_path.expanduser().resolve()


    def _find_entry_for_env(self, env_path):
        for _, (p, entry) in self.aliases_envs.items():
            if Path(p).expanduser().resolve() == env_path:
                return entry
        return None


    def _resolve_password(self, entry, typed_pw):
        cached_pw = entry.get("irodsa_backup") if entry else None

        if not cached_pw and not typed_pw:
            self.error_label.setText("Password required for this environment.")
            return None

        if cached_pw and typed_pw == "***********":
            return cached_pw

        return typed_pw


    def _validate_env_config(self, env_path):
        msg = check_irods_config(env_path, include_network=False)
        if msg != "All checks passed successfully.":
            self.error_label.setText("Go to menu Configure.\n" + msg)
            return False
        return True


    def _create_session(self, env_path, typed_pw, password):
        if typed_pw == "***********":
            with open(IRODSA, "w", encoding="utf-8", opener=self.strictwrite) as f:
                f.write(password)
            return Session(irods_env=env_path)

        return Session(irods_env=env_path, password=password)

    def _on_connect(self):
        self.error_label.clear()

        # Parse environment
        env_info = self._get_env_selection()
        if env_info is None:
            return
        alias, env_path = env_info

        # Find entry
        entry = self._find_entry_for_env(env_path)

        # Resolve password
        typed_pw = self.password_field.text()
        password = self._resolve_password(entry, typed_pw)
        if password is None:
            return

        # Validate environment config
        if not self._validate_env_config(env_path):
            return

        try:
            session = self._create_session(env_path, typed_pw, password)
            # Validate home
            if not self.session_manager.check_home(session):
                self.error_label.setText(f'"irods_home": "{session.home}" does not exist.')
                return

            # Validate resource
            if not self.session_manager.check_resource(session):
                self.error_label.setText(
                    f'"irods_default_resource": "{session.default_resc}" not writeable.'
                )
                return

            # Success
            self.accepted_credentials = {
                "session": session,
                "alias": alias,
                "env_path": env_path,
            }
            self.session_manager.config_manager.save_current_settings(env_path)
            self.session_manager.config_manager.set_last_ienv(alias, str(env_path))

            self.accept()

        except LoginError as err:
            self.logger.error("LoginError: %s", err)
            self.error_label.setText("irods_environment.json not setup correctly.")

        except PasswordError:
            self.logger.warning("PasswordError: wrong password")
            self.error_label.setText("Wrong password!")

        except ConnectionError as err:
            self.logger.error("ConnectionError: %s", err)
            self.error_label.setText(
                "Cannot connect to server. Check Internet, host name and port."
            )

        except ResourceDoesNotExist as err:
            self.logger.error("ResourceDoesNotExist: %s", err)
            self.error_label.setText('"irods_default_resource" does not exist.')

        except Exception as err:
            self.logger.exception("Unexpected error during login")
            self.error_label.setText(f"Login failed: {err!r}")


    def _parse_envbox_text(self) -> tuple[str | None, Path] | None:
        """Return (alias, path) where alias may be None."""
        env_text = self.envbox.currentText().strip()
        if not env_text:
            self.error_label.setText("No environment selected")
            return None

        # Case 1: "alias - /path/to/env.json"
        if " - " in env_text:
            alias, path_str = env_text.split(" - ", 1)
            alias = alias.strip()
        else:
            # Case 2: "/path/to/env.json"
            alias = None
            path_str = env_text
        path_str = path_str.strip()

        return alias, Path(path_str).expanduser()


    def strictwrite(self, path, flags, mode=0o600):
        """Create opener for the standard open command to modify the umask."""
        return os.open(path, flags, mode)
