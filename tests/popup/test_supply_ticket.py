"""Tests for the SupplyTicket dialog."""

import posixpath
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PySide6 import QtCore

from ibridgesgui.popup_widgets import supply_ticket
from ibridgesgui.popup_widgets.supply_ticket import SupplyTicket

MODULE = "ibridgesgui.popup_widgets.supply_ticket"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def session():
    return SimpleNamespace(home="/zone/home/user")


@pytest.fixture
def session_manager(session):
    return SimpleNamespace(session=session, session_changed=MagicMock())


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def dialog(qtbot, session_manager, logger, monkeypatch):
    dlg = SupplyTicket(session_manager, logger)
    qtbot.addWidget(dlg)
    # Record calls to done() instead of closing the dialog.
    dlg.done_calls = []
    monkeypatch.setattr(dlg, "done", lambda code: dlg.done_calls.append(code))
    return dlg


@pytest.fixture
def fake_paths(monkeypatch):
    """Replace IrodsPath; tests choose which paths exist."""
    state = SimpleNamespace(collections=set(), dataobjects=set())

    class FakeIrodsPath:
        def __init__(self, session, path):
            self.session = session
            self._path = path

        def collection_exists(self):
            return self._path in state.collections

        def dataobject_exists(self):
            return self._path in state.dataobjects

        @property
        def parent(self):
            return FakeIrodsPath(self.session, posixpath.dirname(self._path))

        def __str__(self):
            return self._path

    monkeypatch.setattr(f"{MODULE}.IrodsPath", FakeIrodsPath)
    return state


@pytest.fixture
def ticket_calls(monkeypatch):
    """Replace TicketAccess; records (session, ticket_str, irods_path) per call."""
    calls = []

    class FakeTicketAccess:
        def __init__(self, session, ticket_str, irods_path=None, supply=True):
            self.ticket_str = ticket_str
            calls.append((session, ticket_str, irods_path))

    monkeypatch.setattr(f"{MODULE}.TicketAccess", FakeTicketAccess)
    return calls


def _fill(dialog, path, ticket):
    dialog.irods_path.setText(path)
    dialog.ticket_string.setText(ticket)


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


def test_init(dialog, session_manager, logger):
    assert dialog.windowTitle() == "Supply Ticket"
    assert bool(dialog.windowFlags() & QtCore.Qt.WindowType.WindowStaysOnTopHint)
    assert dialog.session_manager is session_manager
    assert dialog.logger is logger


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["", "   "])
def test_accept_requires_path(dialog, session_manager, ticket_calls, fake_paths, path):
    _fill(dialog, path, "kpIwGA1UZN0LFnM")
    dialog.accept()

    assert "irods path" in dialog.error_label.text()
    assert ticket_calls == []
    session_manager.session_changed.emit.assert_not_called()
    assert dialog.done_calls == []


@pytest.mark.parametrize("ticket", ["", "   "])
def test_accept_requires_ticket(dialog, session_manager, ticket_calls, fake_paths, ticket):
    _fill(dialog, "/zone/home/user/coll", ticket)
    dialog.accept()

    assert "ticket" in dialog.error_label.text()
    assert ticket_calls == []
    session_manager.session_changed.emit.assert_not_called()
    assert dialog.done_calls == []


def test_accept_clears_previous_error(dialog, ticket_calls, fake_paths):
    dialog.error_label.setText("old error")
    fake_paths.collections.add("/zone/home/user/coll")
    _fill(dialog, "/zone/home/user/coll", "abc")
    dialog.accept()

    assert dialog.error_label.text() == ""


# ---------------------------------------------------------------------------
# Successful supply
# ---------------------------------------------------------------------------


def test_accept_collection(dialog, session, session_manager, logger, ticket_calls, fake_paths):
    fake_paths.collections.add("/zone/home/user/coll")
    _fill(dialog, "/zone/home/user/coll", "abc")
    dialog.accept()

    assert ticket_calls[-1][1] == "abc"
    assert str(ticket_calls[-1][2]) == "/zone/home/user/coll"
    assert session.home == "/zone/home/user/coll"
    session_manager.session_changed.emit.assert_called_once_with(session)
    logger.info.assert_called_once()
    assert len(dialog.done_calls) == 1
    assert dialog.error_label.text() == ""


def test_accept_dataobject_uses_parent_as_home(
    dialog, session, session_manager, logger, ticket_calls, fake_paths
):
    fake_paths.dataobjects.add("/zone/home/user/coll/file.txt")
    _fill(dialog, "/zone/home/user/coll/file.txt", "abc")
    dialog.accept()

    assert session.home == "/zone/home/user/coll"
    session_manager.session_changed.emit.assert_called_once_with(session)
    logger.info.assert_called_once()
    assert len(dialog.done_calls) == 1


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_accept_path_does_not_exist(dialog, session, session_manager, ticket_calls, fake_paths):
    _fill(dialog, "/zone/home/user/missing", "abc")
    dialog.accept()

    text = dialog.error_label.text()
    assert "abc" in text
    assert "/zone/home/user/missing" in text
    assert session.home == "/zone/home/user"  # unchanged
    session_manager.session_changed.emit.assert_not_called()
    assert dialog.done_calls == []


@pytest.mark.xfail(
    strict=True,
    raises=ValueError,
    reason="accept() creates a TicketAccess outside the try block, so its errors are not shown.",
)
def test_accept_shows_ticket_access_error(dialog, session_manager, fake_paths, monkeypatch):
    def raising(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(f"{MODULE}.TicketAccess", raising)
    fake_paths.collections.add("/zone/home/user/coll")
    _fill(dialog, "/zone/home/user/coll", "abc")
    dialog.accept()

    assert dialog.error_label.text() == "boom"
    session_manager.session_changed.emit.assert_not_called()
    assert dialog.done_calls == []
