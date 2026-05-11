import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication

from ibridgesgui.mainmenu.main_window import MainWindow


@pytest.fixture
def fake_config():
    cfg = MagicMock()
    cfg.load_tabs.return_value = ["Home", "Data"]
    return cfg


@pytest.fixture
def fake_session():
    s = MagicMock()
    s.home = "/zone/home/user"
    s.default_resc = "resc"
    return s


@pytest.fixture
def main_window(qtbot, fake_config):
    """Create a MainWindow with all external dependencies mocked."""
    win = MainWindow(app_name="TestApp", config_manager=fake_config)
    qtbot.addWidget(win)

    # Patch tab_manager to avoid real widgets
    win.tab_manager.load_tab = MagicMock()
    win.tab_manager.unload_tab = MagicMock()
    win.tab_manager.restore_tabs = MagicMock()
    win.tab_manager.loaded_tabs = {}

    return win


# ---------------------------------------------------------------------------
# Basic initialization
# ---------------------------------------------------------------------------

def test_initial_state(main_window):
    assert main_window.menuPlugins.isEnabled() is False
    assert main_window.tab_widget.count() == 1  # Welcome tab


# ---------------------------------------------------------------------------
# Session changed: login
# ---------------------------------------------------------------------------

def test_on_session_changed_login(main_window, fake_session):
    main_window.on_session_changed(fake_session)

    assert main_window.menuPlugins.isEnabled() is True
    main_window.tab_manager.restore_tabs.assert_called_once()


# ---------------------------------------------------------------------------
# Session changed: logout
# ---------------------------------------------------------------------------

def test_on_session_changed_logout(main_window):
    main_window.on_session_changed(None)

    assert main_window.menuPlugins.isEnabled() is False
    assert main_window.tab_widget.count() == 1  # Welcome tab
    assert main_window.tab_manager.loaded_tabs == {}


# ---------------------------------------------------------------------------
# Prevent duplicate sessions
# ---------------------------------------------------------------------------

def test_on_connect_prevent_duplicate(main_window, qtbot, fake_session, monkeypatch):
    # Pretend a session already exists
    main_window.session_manager.session = fake_session

    monkeypatch.setattr(
        "PySide6.QtWidgets.QMessageBox.information",
        lambda *a, **k: None
    )

    called = False

    def fake_connect(parent):
        nonlocal called
        called = True

    monkeypatch.setattr(main_window.session_manager, "connect", fake_connect)

    main_window._on_connect()

    assert called is False  # connect() must NOT be called


# ---------------------------------------------------------------------------
# Allow connect when no session exists
# ---------------------------------------------------------------------------

def test_on_connect_opens_login(main_window, monkeypatch):
    main_window.session_manager.session = None

    called = False

    def fake_connect(parent):
        nonlocal called
        called = True

    monkeypatch.setattr(main_window.session_manager, "connect", fake_connect)

    main_window._on_connect()

    assert called is True


# ---------------------------------------------------------------------------
# Disconnect clears session and tabs
# ---------------------------------------------------------------------------

def test_on_disconnect(main_window, fake_session):
    main_window.session_manager.session = fake_session

    # Patch disconnect
    main_window.session_manager.disconnect = MagicMock()

    main_window._on_disconnect()

    main_window.session_manager.disconnect.assert_called_once()


# ---------------------------------------------------------------------------
# Toggle tab behavior
# ---------------------------------------------------------------------------

def test_toggle_tab_load(main_window, fake_session):
    main_window.session_manager.session = fake_session
    main_window.tab_manager.loaded_tabs = {}

    main_window._toggle_tab("Home")

    main_window.tab_manager.load_tab.assert_called_once()


def test_toggle_tab_unload(main_window, fake_session):
    main_window.session_manager.session = fake_session
    main_window.tab_manager.loaded_tabs = {"Home": MagicMock()}

    main_window._toggle_tab("Home")

    main_window.tab_manager.unload_tab.assert_called_once()

