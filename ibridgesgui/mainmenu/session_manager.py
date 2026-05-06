"""Manage ibridges connection."""
from __future__ import annotations

from ibridges import IrodsPath, Session
from ibridges.resources import Resources
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog

from ibridgesgui.login import LoginDialog


class SessionManager(QObject):
    """Handles iRODS session lifecycle, password caching, and logging."""

    session_changed = Signal(object)

    def __init__(self, config_manager, logger):
        """Init."""
        super().__init__()
        self.config_manager = config_manager
        self.logger = logger
        self.session: Session | None = None

    def connect(self, parent=None):
        """Get session from Login."""
        dialog = LoginDialog(parent, self.logger, self)
        if dialog.exec() != QDialog.Accepted:
            return

        creds = dialog.accepted_credentials
        session = creds["session"]

        self.session = session
        self.session_changed.emit(session)

    def disconnect(self) -> None:
        """Close connecion."""
        if self.session is not None:
            self.logger.info("Closing session.")
            self.session.close()
            self.session = None
            self.session_changed.emit(None)

    # Validation helpers
    def check_home(self, session: Session) -> bool:
        """Check home path exists."""
        try:
            return IrodsPath(session, session.home).collection_exists()
        except Exception:
            return False

    def check_resource(self, session: Session) -> bool:
        """Check default resource exists."""
        try:
            resc = Resources(session).get_resource(session.default_resc)
            return not resc.parent
        except Exception:
            return False
