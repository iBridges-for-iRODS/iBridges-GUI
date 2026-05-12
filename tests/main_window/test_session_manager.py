import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QDialog

from ibridgesgui.mainmenu.session_manager import SessionManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_logger():
    return MagicMock()


@pytest.fixture
def fake_config_manager():
    cm = MagicMock()
    cm.save_current_settings = MagicMock()
    cm.set_last_ienv = MagicMock()
    return cm


@pytest.fixture
def manager(fake_config_manager, fake_logger):
    return SessionManager(fake_config_manager, fake_logger)


@pytest.fixture
def fake_session():
    s = MagicMock()
    s.home = "/zone/home/user"
    s.default_resc = "resc"
    return s


# ---------------------------------------------------------------------------
# connect()
# ---------------------------------------------------------------------------

def test_connect_accept(monkeypatch, manager, fake_session):
    """LoginDialog returns Accepted → session is set and signal emitted."""

    # Fake LoginDialog
    class FakeDialog:
        def __init__(self, parent, logger, sm):
            self.accepted_credentials = {"session": fake_session}

        def exec(self):
            return QDialog.Accepted

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.LoginDialog", FakeDialog)

    received = []

    def on_changed(s):
        received.append(s)

    manager.session_changed.connect(on_changed)

    manager.connect()

    assert manager.session is fake_session
    assert received == [fake_session]


def test_connect_rejected(monkeypatch, manager):
    """LoginDialog returns Rejected → no session created."""

    class FakeDialog:
        def __init__(self, parent, logger, sm):
            pass

        def exec(self):
            return QDialog.Rejected

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.LoginDialog", FakeDialog)

    manager.connect()

    assert manager.session is None


# ---------------------------------------------------------------------------
# disconnect()
# ---------------------------------------------------------------------------

def test_disconnect_success(manager, fake_session):
    """disconnect() closes session, clears state, and emits signal."""

    manager.session = fake_session
    fake_session.close = MagicMock()

    received = []

    def on_changed(s):
        received.append(s)

    manager.session_changed.connect(on_changed)

    manager.disconnect()

    fake_session.close.assert_called_once()
    assert manager.session is None
    assert received == [None]


def test_disconnect_error_during_close(manager, fake_session):
    """disconnect() should swallow close() errors and still reset state."""

    manager.session = fake_session
    fake_session.close = MagicMock(side_effect=RuntimeError("boom"))

    received = []
    manager.session_changed.connect(lambda s: received.append(s))

    manager.disconnect()

    assert manager.session is None
    assert received == [None]


# ---------------------------------------------------------------------------
# check_home()
# ---------------------------------------------------------------------------

def test_check_home_true(monkeypatch, manager, fake_session):
    """check_home returns True when collection_exists() is True."""

    class FakeIrodsPath:
        def __init__(self, session, home):
            pass

        def collection_exists(self):
            return True

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.IrodsPath", FakeIrodsPath)

    assert manager.check_home(fake_session) is True


def test_check_home_false(monkeypatch, manager, fake_session):
    """check_home returns False when collection_exists() is False."""

    class FakeIrodsPath:
        def __init__(self, session, home):
            pass

        def collection_exists(self):
            return False

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.IrodsPath", FakeIrodsPath)

    assert manager.check_home(fake_session) is False


def test_check_home_exception(monkeypatch, manager, fake_session):
    """check_home returns False on exception."""

    class FakeIrodsPath:
        def __init__(self, session, home):
            raise RuntimeError("boom")

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.IrodsPath", FakeIrodsPath)

    assert manager.check_home(fake_session) is False


# ---------------------------------------------------------------------------
# check_resource()
# ---------------------------------------------------------------------------

def test_check_resource_true(monkeypatch, manager, fake_session):
    """check_resource returns True when resource has no parent."""

    class FakeResc:
        parent = None

    class FakeResources:
        def __init__(self, session):
            pass

        def get_resource(self, name):
            return FakeResc()

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.Resources", FakeResources)

    assert manager.check_resource(fake_session) is True


def test_check_resource_false(monkeypatch, manager, fake_session):
    """check_resource returns False when resource has a parent."""

    class FakeResc:
        parent = "something"

    class FakeResources:
        def __init__(self, session):
            pass

        def get_resource(self, name):
            return FakeResc()

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.Resources", FakeResources)

    assert manager.check_resource(fake_session) is False


def test_check_resource_exception(monkeypatch, manager, fake_session):
    """check_resource returns False on exception."""

    class FakeResources:
        def __init__(self, session):
            pass

        def get_resource(self, name):
            raise RuntimeError("boom")

    monkeypatch.setattr("ibridgesgui.mainmenu.session_manager.Resources", FakeResources)

    assert manager.check_resource(fake_session) is False

