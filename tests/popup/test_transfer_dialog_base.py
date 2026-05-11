import pytest
from PySide6 import QtWidgets, QtGui
from ibridgesgui.popup_widgets.base import TransferDialogBase

@pytest.fixture
def dialog(qtbot):
    d = TransferDialogBase()
    qtbot.addWidget(d)
    d.show()
    return d

def test_close_event_blocks_when_active(dialog, qtbot):
    dialog.active_transfer = True
    event = QtGui.QCloseEvent()
    dialog.closeEvent(event)
    assert event.isAccepted() is False

def test_close_event_allows_when_inactive(dialog, qtbot):
    dialog.active_transfer = False
    event = QtGui.QCloseEvent()
    dialog.closeEvent(event)
    assert event.isAccepted() is True

def test_close_method_respects_close_event(dialog, qtbot):
    dialog.active_transfer = True
    dialog.close()
    assert dialog.isVisible()

def test_close_method_closes_when_inactive(dialog, qtbot):
    dialog.active_transfer = False
    dialog.close()
    assert not dialog.isVisible()

