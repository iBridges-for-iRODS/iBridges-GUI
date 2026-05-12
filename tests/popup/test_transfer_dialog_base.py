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
    class FakeThread:
        def isRunning(self):
            return True

    dialog.transfer_thread = FakeThread()
    event = QtGui.QCloseEvent()
    dialog.closeEvent(event)
    assert event.isAccepted() is False

def test_close_event_allows_when_inactive(dialog, qtbot):
    class FakeThread:
        def isRunning(self):
            return False

    dialog.transfer_thread = FakeThread()
    event = QtGui.QCloseEvent()
    dialog.closeEvent(event)
    assert event.isAccepted() is True

def test_close_method_respects_close_event(dialog, qtbot):
    class FakeThread:
        def isRunning(self):
            return True

    dialog.transfer_thread = FakeThread()
    dialog.close()
    assert dialog.isVisible()

def test_close_method_closes_when_inactive(dialog, qtbot):
    class FakeThread:
        def isRunning(self):
            return False

    dialog.transfer_thread = FakeThread()
    dialog.close()
    assert not dialog.isVisible()

