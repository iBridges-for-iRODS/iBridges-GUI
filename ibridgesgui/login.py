from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QDialog, QMessageBox, QLineEdit
from irods.exception import ResourceDoesNotExist
from ibridges import Session
from ibridges.session import LoginError, PasswordError
from ibridges.cli.config import IbridgesConf
from ibridgesgui.config import get_last_ienv_name, load_envs_from_cli_and_fs, check_irods_config
from ibridgesgui.config import IRODSA
from ibridgesgui.ui_files.irodsLogin import Ui_irodsLogin


class LoginDialog(QDialog, Ui_irodsLogin):
    """Login dialog that loads an iRODS environment file and collects password."""

    def __init__(self, parent=None, logger=None, session_manager=None) -> None:
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
    
        alias, env_path = parsed
        env_path = env_path.expanduser().resolve()
    
        entry = None
        for a, (p, e) in self.aliases_envs.items():
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
    
    def _on_connect(self):
        self.error_label.clear()
    
        parsed = self._parse_envbox_text()
        if parsed is None:
            self.error_label.setText("No environment selected.")
            return
    
        alias, env_path = parsed
        env_path = env_path.expanduser().resolve()
    
        # Find entry
        entry = None
        for a, (p, e) in self.aliases_envs.items():
            if Path(p).expanduser().resolve() == env_path:
                entry = e
                break
    
        cached_pw = entry.get("irodsa_backup") if entry else None
        typed_pw = self.password_field.text()
    
        if not cached_pw and not typed_pw:
            self.error_label.setText("Password required for this environment.")
            return
    
        msg = check_irods_config(env_path, include_network=False)
        if msg != "All checks passed successfully.":
            self.error_label.setText("Go to menu Configure.\n" + msg)
            return
    
        try:
            # Use cached password
            if cached_pw and typed_pw == "***********":
                with open(IRODSA, "w", encoding="utf-8", opener=self.strictwrite) as f:
                    f.write(cached_pw)
                session = Session(irods_env=env_path)
            else:
                session = Session(irods_env=env_path, password=typed_pw)
    
            # Validate home and resource
            if not self.session_manager._check_home(session):
                self.error_label.setText(f'"irods_home": "{session.home}" does not exist.')
                return
    
            if not self.session_manager._check_resource(session):
                self.error_label.setText(
                    f'"irods_default_resource": "{session.default_resc}" not writeable.'
                )
                return
    
            # Success → return session to SessionManager
            self.accepted_credentials = {
                "session": session,
                "alias": alias,
                "env_path": env_path,
            }
            self.session_manager.config_manager.save_current_settings(env_path)
            path = str(env_path)
            self.session_manager.config_manager.set_last_ienv(alias, path)
 
            self.accept()
    
        except LoginError as err:
            self.logger.error("LoginError: %s", err)
            self.error_label.setText("irods_environment.json not setup correctly.")
        
        except PasswordError as err:
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
        """
        Returns (alias, path) where alias may be None.
        """
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
