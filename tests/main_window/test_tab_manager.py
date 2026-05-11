import pytest
from unittest.mock import MagicMock

from ibridgesgui.mainmenu.tab_manager import TabManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_tab_widget():
    """Mock QTabWidget-like object."""
    tw = MagicMock()
    tw.addTab = MagicMock()
    tw.removeTab = MagicMock()
    tw.indexOf = MagicMock(return_value=0)
    return tw


@pytest.fixture
def fake_plugin_manager():
    pm = MagicMock()
    pm.get_provider = MagicMock(return_value=lambda *a: "PLUGIN_WIDGET")
    return pm


@pytest.fixture
def fake_config():
    cfg = MagicMock()
    cfg.save_tabs = MagicMock()
    cfg.load_tabs = MagicMock(return_value=["Browser", "Search", "PluginTab"])
    return cfg


@pytest.fixture
def fake_main_window():
    """Mock main window with plugin_actions dict."""
    mw = MagicMock()
    mw.plugin_actions = {
        "Browser": MagicMock(),
        "Synchronise Data": MagicMock(),
        "Search": MagicMock(),
        "Info": MagicMock(),
        "Logs": MagicMock(),
        "PluginTab": MagicMock(),
    }
    return mw



@pytest.fixture
def manager(monkeypatch, fake_tab_widget, fake_plugin_manager, fake_config, fake_main_window):

    # Patch the names INSIDE tab_manager.py
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.tab_manager.Search",
        lambda *args, **kwargs: "SEARCH_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.tab_manager.Browser",
        lambda *args, **kwargs: "BROWSER_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.tab_manager.Sync",
        lambda *args, **kwargs: "SYNC_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.tab_manager.Info",
        lambda *args, **kwargs: "INFO_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.tab_manager.LogViewer",
        lambda *args, **kwargs: "LOG_WIDGET"
    )

    # ALSO patch the original modules (safety net)
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search.Search",
        lambda *args, **kwargs: "SEARCH_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.browsertab.browser.Browser",
        lambda *args, **kwargs: "BROWSER_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.synctab.sync.Sync",
        lambda *args, **kwargs: "SYNC_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.info.Info",
        lambda *args, **kwargs: "INFO_WIDGET"
    )
    monkeypatch.setattr(
        "ibridgesgui.logviewer.LogViewer",
        lambda *args, **kwargs: "LOG_WIDGET"
    )

    return TabManager(fake_tab_widget, fake_plugin_manager, fake_config, fake_main_window)


@pytest.fixture
def fake_session():
    return MagicMock()


# ---------------------------------------------------------------------------
# load_tab()
# ---------------------------------------------------------------------------

def test_load_standard_tab(manager, fake_tab_widget, fake_session):
    manager.load_tab("Browser", fake_session, "App", MagicMock())

    assert "Browser" in manager.loaded_tabs
    fake_tab_widget.addTab.assert_called_once()
    manager.config.save_tabs.assert_called_once()


def test_load_plugin_tab(manager, fake_tab_widget, fake_session, fake_plugin_manager):
    manager.load_tab("PluginTab", fake_session, "App", MagicMock())

    assert "PluginTab" in manager.loaded_tabs
    fake_plugin_manager.get_provider.assert_called_once_with("PluginTab")
    fake_tab_widget.addTab.assert_called_once()


def test_load_tab_twice(manager, fake_session):
    manager.loaded_tabs["Browser"] = "WIDGET"

    manager.load_tab("Browser", fake_session, "App", MagicMock())

    # Should NOT load again
    assert manager.tab_widget.addTab.call_count == 0


# ---------------------------------------------------------------------------
# unload_tab()
# ---------------------------------------------------------------------------

def test_unload_tab(manager, fake_tab_widget):
    manager.loaded_tabs["Browser"] = "WIDGET"

    manager.unload_tab("Browser")

    fake_tab_widget.removeTab.assert_called_once()
    assert "Browser" not in manager.loaded_tabs
    manager.config.save_tabs.assert_called()


def test_unload_missing_tab(manager):
    manager.unload_tab("MissingTab")  # should not crash
    manager.tab_widget.removeTab.assert_not_called()


# ---------------------------------------------------------------------------
# restore_tabs()
# ---------------------------------------------------------------------------

def test_restore_tabs(manager, fake_session):
    """
    restore_tabs loads:
    - standard tabs in standard order
    - plugin tabs afterwards
    """
    manager.restore_tabs(fake_session, "App", MagicMock())

    # Expected order: Browser, Search, PluginTab
    assert list(manager.loaded_tabs.keys()) == ["Browser", "Search", "PluginTab"]


def test_restore_tabs_default_when_empty(manager, fake_config, fake_session):
    fake_config.load_tabs.return_value = []

    manager.restore_tabs(fake_session, "App", MagicMock())

    # Should load ALL standard tabs in order
    assert list(manager.loaded_tabs.keys()) == list(manager.standard_tabs.keys())


# ---------------------------------------------------------------------------
# update_plugin_menu()
# ---------------------------------------------------------------------------

def test_update_plugin_menu(manager, fake_main_window):
    manager.loaded_tabs = {"Browser": "WIDGET"}

    manager.update_plugin_menu()

    # Browser should be checked, others unchecked
    for name, action in fake_main_window.plugin_actions.items():
        if name == "Browser":
            action.setChecked.assert_called_with(True)
        else:
            action.setChecked.assert_called_with(False)

