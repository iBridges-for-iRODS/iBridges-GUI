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
        """Fully close the session and reset GUI + session manager state."""
        if self.session is not None:
            self.logger.info("Closing session.")
    
            try:
                self.session.close()
            except Exception as err:
                self.logger.warning("Error closing session: %s", err)
    
            # Remove session from this object
            self.session = None

            # Reset session manager state
            if hasattr(self, "session_manager"):
                self.session_manager.session = None
    
            # Emit signal so GUI components reset themselves
            self.session_changed.emit(None)
    
            # Optional: force GUI refresh
            if hasattr(self, "refresh"):
                self.refresh()
    
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
