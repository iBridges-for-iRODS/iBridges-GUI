"""Tests for the ticket editor popup (popup_widgets/manage_tickets.py)."""

import posixpath
from datetime import datetime
from types import SimpleNamespace

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from ibridges.tickets import TicketData
from ibridgesgui.popup_widgets.manage_tickets import TicketEditor

MODULE = "ibridgesgui.popup_widgets.manage_tickets"
HOME = "/tempZone/home/testuser"
DATA = f"{HOME}/data"
USER_ROLE = QtCore.Qt.ItemDataRole.UserRole


# ---------------------------------------------------------------------------
# Fakes: iRODS paths, tree model and tickets
# ---------------------------------------------------------------------------


@pytest.fixture
def world(monkeypatch):
    """Replace IrodsPath, IrodsTreeModel and Tickets in the module.

    The returned namespace holds the state the fakes work with:
    ``existing`` (paths that exist), ``tickets`` (tickets on the "server"),
    ``created`` / ``deleted`` (recorded calls) and ``create_error`` /
    ``delete_error`` (set to an exception to make the call fail).
    """
    state = SimpleNamespace(
        existing={"/", "/tempZone", "/tempZone/home", HOME, DATA},
        tickets=[
            TicketData("tick1", "read", DATA, datetime(2030, 1, 1)),
            TicketData("tick2", "write", HOME, ""),
        ],
        created=[],
        deleted=[],
        create_error=None,
        delete_error=None,
    )

    class FakeIrodsPath:
        def __init__(self, session, path=None):
            self.session = session
            self._path = str(path) if path is not None else session.cwd

        def absolute(self):
            return self

        @property
        def parent(self):
            return FakeIrodsPath(self.session, posixpath.dirname(self._path) or "/")

        def exists(self):
            return self._path in state.existing

        def __str__(self):
            return self._path

    class FakeTreeModel(QtGui.QStandardItemModel):
        def __init__(self, view, root):
            super().__init__(view)
            self.root = root
            self.items = {}  # path -> first-column item
            self.refreshed = []  # paths that were refreshed
            self.setColumnCount(6)

        def init_tree(self):
            def depth(path):
                return 0 if path == "/" else path.count("/")

            for path in sorted(state.existing, key=lambda p: (depth(p), p)):
                item = QtGui.QStandardItem(posixpath.basename(path) or "/")
                item.setData(path, USER_ROLE)
                row = [item] + [QtGui.QStandardItem() for _ in range(5)]
                if path == "/":
                    self.appendRow(row)
                else:
                    self.items[posixpath.dirname(path) or "/"].appendRow(row)
                self.items[path] = item

        def refresh_subtree(self, index):
            self.refreshed.append(index.data(USER_ROLE))

        def index_from_irods_path(self, path):
            item = self.items.get(str(path))
            return item.index() if item is not None else QtCore.QModelIndex()

        def irods_path_from_tree_index(self, index):
            return FakeIrodsPath(self.root.session, index.data(USER_ROLE))

    class FakeTickets:
        def __init__(self, session):
            self.session = session

        def fetch_tickets(self):
            return list(state.tickets)

        def create_ticket(self, irods_path, ticket_type="read", expiry_date=None):
            if state.create_error is not None:
                raise state.create_error
            state.created.append((str(irods_path), ticket_type, expiry_date))
            state.tickets.append(
                TicketData("NEWTICKET", ticket_type, str(irods_path), expiry_date or "")
            )
            return "NEWTICKET", expiry_date is not None

        def delete_ticket(self, ticket, check=False):
            if state.delete_error is not None:
                raise state.delete_error
            state.deleted.append(ticket)
            state.tickets[:] = [t for t in state.tickets if t.name != ticket]

    state.Path = FakeIrodsPath
    monkeypatch.setattr(f"{MODULE}.IrodsPath", FakeIrodsPath)
    monkeypatch.setattr(f"{MODULE}.IrodsTreeModel", FakeTreeModel)
    monkeypatch.setattr(f"{MODULE}.Tickets", FakeTickets)
    return state


@pytest.fixture
def session():
    return SimpleNamespace(home=HOME, cwd=HOME)


@pytest.fixture
def dialog(qtbot, session, fake_logger, world):
    dlg = TicketEditor(session, fake_logger)
    qtbot.addWidget(dlg)
    return dlg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def select_path(dialog, path):
    """Select a path in the tree, like a click would."""
    index = dialog.irods_model.items[path].index()
    dialog.irods_tree_view.selectionModel().select(
        index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
    )
    return index


def logged_levels(logger):
    """Log levels used so far; needs the recording fake_logger from the conftest."""
    return [level for level, _ in logger.calls]


def delete_button(dialog, row):
    return dialog.ticket_table.cellWidget(row, 3).findChild(QtWidgets.QPushButton)


def table_names(dialog):
    table = dialog.ticket_table
    return [table.item(row, 0).text() for row in range(table.rowCount())]


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


def test_init_window(dialog, session, fake_logger):
    assert bool(dialog.windowFlags() & QtCore.Qt.WindowType.WindowStaysOnTopHint)
    assert dialog.session is session
    assert dialog.logger is fake_logger


def test_init_fills_ticket_table(dialog):
    assert table_names(dialog) == ["tick1", "tick2"]


def test_init_ticket_table_header(dialog):
    header = dialog.ticket_table.horizontalHeader()

    assert header.sectionResizeMode(0) == QtWidgets.QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(3) == QtWidgets.QHeaderView.ResizeMode.Fixed


def test_init_expiry_calendar_follows_checkbox(dialog):
    assert dialog.expiry_calendar.isEnabled() == (not dialog.expiry_checkbox.isChecked())

    dialog.expiry_checkbox.setChecked(True)
    assert not dialog.expiry_calendar.isEnabled()

    dialog.expiry_checkbox.setChecked(False)
    assert dialog.expiry_calendar.isEnabled()


def test_close_button_closes_dialog(qtbot, dialog):
    dialog.show()
    assert dialog.isVisible()

    dialog.close_button.click()

    assert not dialog.isVisible()


# ---------------------------------------------------------------------------
# iRODS tree
# ---------------------------------------------------------------------------


def test_irods_root_is_top_of_tree(dialog):
    assert str(dialog._irods_root()) == "/"


def test_tree_view_setup(dialog):
    view = dialog.irods_tree_view

    assert view.model() is dialog.irods_model
    assert view.isHeaderHidden()
    assert all(view.isColumnHidden(col) for col in (1, 2, 3, 4, 5))
    assert not view.isColumnHidden(0)


def test_tree_expanded_to_home_and_home_selected(dialog):
    model = dialog.irods_model
    view = dialog.irods_tree_view

    current = view.currentIndex()
    assert current.isValid()
    assert str(model.irods_path_from_tree_index(current)) == HOME
    for parent in ("/", "/tempZone", "/tempZone/home"):
        assert view.isExpanded(model.items[parent].index())
        assert parent in model.refreshed


def test_expand_path_returns_deepest_existing_node(dialog, session, world):
    missing = world.Path(session, f"{HOME}/missing/deeper")

    index = dialog._expand_path(missing)

    assert index.data(USER_ROLE) == HOME


def test_expand_path_on_empty_model(dialog, session, world):
    dialog.irods_model.clear()

    index = dialog._expand_path(world.Path(session, HOME))

    assert not index.isValid()


def test_expand_to_home_on_empty_model(dialog):
    dialog.irods_model.clear()
    dialog.irods_tree_view.setCurrentIndex(QtCore.QModelIndex())

    dialog._expand_to_home()

    assert not dialog.irods_tree_view.currentIndex().isValid()


def test_expanding_a_node_refreshes_it(dialog):
    model = dialog.irods_model
    model.refreshed.clear()

    dialog.irods_tree_view.collapse(model.items[HOME].index())
    dialog.irods_tree_view.expand(model.items[HOME].index())

    assert HOME in model.refreshed


# ---------------------------------------------------------------------------
# Ticket table
# ---------------------------------------------------------------------------


def test_ticket_table_rows(dialog):
    table = dialog.ticket_table

    assert table.rowCount() == 2
    assert [table.item(0, col).text() for col in range(3)] == [
        "tick1",
        DATA,
        str(datetime(2030, 1, 1)),
    ]
    assert table.item(0, 1).toolTip() == DATA
    # A ticket without an expiry date shows "never".
    assert [table.item(1, col).text() for col in range(3)] == ["tick2", HOME, "never"]


def test_ticket_table_has_delete_buttons(dialog):
    for row in range(dialog.ticket_table.rowCount()):
        assert delete_button(dialog, row) is not None


def test_refresh_replaces_rows(dialog, world):
    dialog._refresh_ticket_table()
    assert table_names(dialog) == ["tick1", "tick2"]

    world.tickets.append(TicketData("tick3", "read", DATA, ""))
    dialog._refresh_ticket_table()

    assert table_names(dialog) == ["tick1", "tick2", "tick3"]


def test_refresh_with_no_tickets(dialog, world):
    world.tickets.clear()

    dialog._refresh_ticket_table()

    assert dialog.ticket_table.rowCount() == 0


# ---------------------------------------------------------------------------
# Deleting tickets
# ---------------------------------------------------------------------------


def test_delete_button_deletes_its_own_ticket(dialog, world, fake_logger):
    delete_button(dialog, 1).click()

    assert world.deleted == ["tick2"]
    assert table_names(dialog) == ["tick1"]
    assert dialog.error_label.text() == ""
    assert logged_levels(fake_logger) == ["info"]


def test_delete_buttons_still_match_after_rows_shift(dialog, world):
    delete_button(dialog, 0).click()  # removes tick1, tick2 moves to row 0
    delete_button(dialog, 0).click()

    assert world.deleted == ["tick1", "tick2"]
    assert dialog.ticket_table.rowCount() == 0


def test_delete_clears_previous_error(dialog):
    dialog.error_label.setText("old error")

    dialog.delete_ticket("tick1")

    assert dialog.error_label.text() == ""


def test_delete_error_is_shown(dialog, world, fake_logger):
    world.delete_error = RuntimeError("cannot delete")

    dialog.delete_ticket("tick1")

    assert dialog.error_label.text() == "cannot delete"
    assert logged_levels(fake_logger) == ["error"]
    assert table_names(dialog) == ["tick1", "tick2"]  # unchanged


# ---------------------------------------------------------------------------
# Creating tickets
# ---------------------------------------------------------------------------


def test_create_requires_selection(dialog, world):
    dialog.irods_tree_view.selectionModel().clearSelection()

    dialog.create_ticket()

    assert dialog.error_label.text() == "Please select an iRODS path."
    assert world.created == []


def test_create_path_missing_in_session(dialog, world):
    select_path(dialog, DATA)
    world.existing.discard(DATA)  # tree and session no longer agree

    dialog.create_ticket()

    assert "do not match" in dialog.error_label.text()
    assert world.created == []


def test_create_read_ticket_with_expiry(dialog, world, fake_logger):
    select_path(dialog, DATA)
    dialog.expiry_checkbox.setChecked(False)
    dialog.write_button.setAutoExclusive(False)
    dialog.write_button.setChecked(False)
    dialog.expiry_calendar.setSelectedDate(QtCore.QDate(2030, 5, 17))

    dialog.create_ticket()

    assert world.created == [(DATA, "read", datetime(2030, 5, 17))]
    assert dialog.error_label.text() == ""
    assert table_names(dialog) == ["tick1", "tick2", "NEWTICKET"]
    assert logged_levels(fake_logger) == ["info"]


def test_create_write_ticket(dialog, world):
    select_path(dialog, DATA)
    dialog.expiry_checkbox.setChecked(False)
    dialog.write_button.setChecked(True)

    dialog.create_ticket()

    assert world.created[0][1] == "write"


def test_create_ticket_without_expiry(dialog, world):
    select_path(dialog, DATA)
    dialog.expiry_checkbox.setChecked(True)

    dialog.create_ticket()

    assert world.created[0][2] is None


def test_create_clears_previous_error(dialog):
    select_path(dialog, DATA)
    dialog.error_label.setText("old error")

    dialog.create_ticket()

    assert dialog.error_label.text() == ""


def test_create_error_is_shown(dialog, world, fake_logger):
    select_path(dialog, DATA)
    world.create_error = ValueError("cannot create")

    dialog.create_ticket()

    assert dialog.error_label.text() == "cannot create"
    assert logged_levels(fake_logger) == ["error"]
    assert table_names(dialog) == ["tick1", "tick2"]  # unchanged


def test_create_button_is_connected(dialog, world):
    select_path(dialog, DATA)
    dialog.expiry_checkbox.setChecked(True)

    dialog.create_ticket_button.click()

    assert len(world.created) == 1


def test_selected_expiry_is_midnight_of_selected_day(dialog):
    dialog.expiry_calendar.setSelectedDate(QtCore.QDate(2030, 5, 17))

    assert dialog._selected_expiry() == datetime(2030, 5, 17)
