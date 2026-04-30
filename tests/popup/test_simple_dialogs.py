import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.create_collection import CreateCollection
from ibridgesgui.popup_widgets.create_directory import CreateDirectory
from ibridgesgui.popup_widgets.rename_item import Rename


def test_create_directory(tmp_path, qtbot):
    d = CreateDirectory(parent=tmp_path)
    qtbot.addWidget(d)
    d.coll_path_input.setText("newdir")
    d.accept()
    assert (tmp_path / "newdir").exists()


def test_rename_item(qtbot, fake_irods_path):
    class DummyPath:
        def __init__(self):
            self.session = fake_irods_path.session
            self.called = False
        def rename(self, new):
            self.called = True
            return new

    dummy = DummyPath()

    d = Rename(dummy, logger=None)
    qtbot.addWidget(d)
    d.item_path_input.setText("newpath")
    d.accept()

    assert dummy.called

