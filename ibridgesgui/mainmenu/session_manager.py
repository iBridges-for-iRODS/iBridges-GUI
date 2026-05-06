from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QMessageBox
from irods.exception import ResourceDoesNotExist
from ibridges.session import LoginError, PasswordError
from ibridges import Session, IrodsPath
from ibridges.resources import Resources

from ibridgesgui.login import LoginDialog


class SessionManager(QObject):
    """Handles iRODS session lifecycle, password caching, and logging."""

    session_changed = Signal(object)

    def __init__(self, config_manager, logger):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logger
        self.session: Session | None = None

    def connect(self, parent=None):
        dialog = LoginDialog(parent, self.logger, self)
        if dialog.exec() != QDialog.Accepted:
            return

        creds = dialog.accepted_credentials
        session = creds["session"]

        self.session = session
        self.session_changed.emit(session)

    def disconnect(self) -> None:
        if self.session is not None:
            self.logger.info("Closing session.")
            self.session.close()
            self.session = None
            self.session_changed.emit(None)

    # Validation helpers
    def _check_home(self, session: Session) -> bool:
        try:
            return IrodsPath(session, session.home).collection_exists()
        except Exception:
            return False

    def _check_resource(self, session: Session) -> bool:
        try:
            resc = Resources(session).get_resource(session.default_resc)
            return not resc.parent
        except Exception:
            return False
