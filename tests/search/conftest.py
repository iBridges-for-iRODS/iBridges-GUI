# tests/search/conftest.py

import pytest
from unittest.mock import MagicMock
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QLabel,
    QTableWidget,
)

from ibridgesgui.searchtab.search_controller import SearchController
from ibridgesgui.searchtab.search_model import SearchModel

@pytest.fixture
def fake_view_search(qtbot):
    class FakeSearchView(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()

            # REAL BUTTONS (controller uses setEnabled + tests use isEnabled)
            self.search_button = QPushButton()
            self.download_button = QPushButton()
            self.clear_button = QPushButton()
            self.load_more_button = QPushButton()
            #self.load_more_button = MagicMock()
            self.load_more_button.show = MagicMock()
            self.load_more_button.hide = MagicMock()

            # TABLE MUST BE MOCKED (tests patch rowCount, setRowCount, currentIndex)
            self.search_table = MagicMock()
            self.search_table.rowCount = MagicMock(return_value=0)
            self.search_table.setRowCount = MagicMock()
            self.search_table.item = MagicMock()
            self.search_table.currentIndex = MagicMock()
            self.search_table.currentIndex.return_value.row.return_value = 0
            self.search_table.selectRow = MagicMock()
            self.search_table.clearSelection = MagicMock()

            # ---- INPUT FIELDS MUST BE MAGICMOCKS ----
            def make_field(value=""):
                f = MagicMock()
                f.text.return_value = value
                return f

            self.search_path_field = make_field()
            self.path_pattern_field = make_field()
            self.checksum_field = make_field()

            self.case_sensitive_box = MagicMock()
            self.case_sensitive_box.isChecked.return_value = False

            # Metadata fields
            self.key1 = make_field()
            self.val1 = make_field()
            self.units1 = make_field()

            self.key2 = make_field()
            self.val2 = make_field()
            self.units2 = make_field()

            self.key3 = make_field()
            self.val3 = make_field()
            self.units3 = make_field()

            self.key4 = make_field()
            self.val4 = make_field()
            self.units4 = make_field()

            # Radio buttons
            self.radio_object = MagicMock()
            self.radio_collection = MagicMock()
            self.radio_object.text.return_value = "Object"
            self.radio_collection.text.return_value = "Collection"
            self.radio_object.isChecked.return_value = True
            self.radio_collection.isChecked.return_value = False

            self.radio_group = MagicMock()
            self.radio_group.checkedButton.return_value = self.radio_object

            # Select all
            self.select_all_box = MagicMock()
            self.select_all_box.isChecked.return_value = False

            # Error label
            self.error_label = MagicMock()
            self.error_label.setText = MagicMock()
            self.error_label.clear = MagicMock()

            # Helper methods
            self.hide_result_elements = MagicMock()
            self.show_result_elements = MagicMock()
            self.display_results = MagicMock()
            self.append_results = MagicMock()
            self.set_wait_cursor = MagicMock()
            self.set_normal_cursor = MagicMock()
            self.ask_download_destination = MagicMock()
            self.get_selected_paths = MagicMock(return_value=[])

    view = FakeSearchView()
    qtbot.addWidget(view)
    return view


@pytest.fixture
def fake_session():
    return MagicMock(name="session")


@pytest.fixture
def fake_browsercontroller():
    browsercontroller = MagicMock()
    browsercontroller._set_path = MagicMock()
    return browsercontroller


@pytest.fixture
def fake_model(fake_session):
    """Fake SearchModel instance."""
    model = MagicMock(spec=SearchModel)
    model.results = []
    model.current_batch = 0
    return model


@pytest.fixture
def controller(fake_view_search, fake_session, fake_browsercontroller, fake_model, monkeypatch):
    """SearchController wired with fake UI, session, model, and browser."""

    import ibridgesgui.searchtab.search_controller as search_controller_module  # adjust

    # Make SearchModel(...) return our fake_model
    def fake_search_model_ctor(session):
        return fake_model

    monkeypatch.setattr(search_controller_module, "SearchModel", fake_search_model_ctor)

    c = SearchController(
        ui=fake_view_search,
        session=fake_session,
        app_name="test_app",
        browsercontroller=fake_browsercontroller,
    )
    # Ensure model is our fake
    c.model = fake_model
    return c

