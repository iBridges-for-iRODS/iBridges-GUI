# tests/test_info_tab.py

import pytest
from unittest.mock import Mock
from ibridgesgui.info import Info


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_session():
    """Create a session mock with all required attributes."""
    session = Mock()
    session.zone = "tempZone"
    session.username = "alice"
    session.get_user_info.return_value = ("rodsuser", ["group1", "group2"])
    session.default_resc = "demoResc"
    session.host = "irods.example.org"
    session.server_version = (4, 3, 1)
    return session


# ---------------------------------------------------------------------------
# Tests: _collect_info
# ---------------------------------------------------------------------------

def test_collect_info(qtbot, monkeypatch):
    """_collect_info should return a correctly structured info dict."""
    session = make_mock_session()

    class DummyResources:
        root_resources = [
            ("rescA", None, 0, None),
            ("rescB", "child", 1, None),
        ]

    monkeypatch.setattr("ibridgesgui.info.Resources", lambda session: DummyResources)

    info_tab = Info(session)
    qtbot.addWidget(info_tab)

    info = info_tab._collect_info()

    assert info["zone"] == "tempZone"
    assert info["username"] == "alice"
    assert info["user_type"] == "rodsuser"
    assert info["groups"] == ["group1", "group2"]
    assert info["default_resc"] == "demoResc"
    assert info["server"] == "irods.example.org"
    assert info["version"] == "4.3.1"
    assert info["resources"] == [
        ("rescA", None, 0, None),
        ("rescB", "child", 1, None),
    ]


# ---------------------------------------------------------------------------
# Tests: _update_ui
# ---------------------------------------------------------------------------

def test_update_ui_populates_widgets(qtbot, monkeypatch):
    """_update_ui should correctly populate labels and table."""
    session = make_mock_session()

    monkeypatch.setattr("ibridgesgui.info.Resources", lambda s: Mock(root_resources=[]))

    info_tab = Info(session)
    qtbot.addWidget(info_tab)

    info = {
        "zone": "tempZone",
        "username": "alice",
        "user_type": "rodsuser",
        "groups": ["group1", "group2"],
        "log_dir": "/tmp/logs",
        "default_resc": "demoResc",
        "server": "irods.example.org",
        "version": "4.3.1",
        "resources": [
            ("rescA", "", 0, ""),
            ("rescB", "", 0, ""),
        ],
    }

    info_tab._update_ui(info)

    assert info_tab.zone_label.text() == "tempZone"
    assert info_tab.user_label.text() == "alice"
    assert info_tab.type_label.text() == "rodsuser"
    assert info_tab.log_label.text() == "/tmp/logs"
    assert info_tab.resc_label.text() == "demoResc"
    assert info_tab.server_label.text() == "irods.example.org"
    assert info_tab.version_label.text() == "4.3.1"
    assert info_tab.resc_table.rowCount() == 2


# ---------------------------------------------------------------------------
# Tests: refresh_info
# ---------------------------------------------------------------------------

def test_refresh_info_calls_collect_and_update(qtbot, monkeypatch):
    session = make_mock_session()

    monkeypatch.setattr("ibridgesgui.info.Resources", lambda s: Mock(root_resources=[]))

    info_tab = Info(session)
    qtbot.addWidget(info_tab)

    called = {"collect": False, "update": False}

    def fake_collect():
        called["collect"] = True
        return {"dummy": True}

    def fake_update(info):
        called["update"] = True
        assert info == {"dummy": True}

    monkeypatch.setattr(info_tab, "_collect_info", fake_collect)
    monkeypatch.setattr(info_tab, "_update_ui", fake_update)

    info_tab.refresh_info()

    assert called["collect"]
    assert called["update"]

