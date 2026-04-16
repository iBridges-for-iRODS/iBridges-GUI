# search_controller.py
from ibridges import IrodsPath

from .search_model import SearchModel
from .irods_search_service import IrodsSearchService


class SearchController:
    """Controller for the Search tab."""

    def __init__(self, ui, session, app_name, browser):
        self.ui = ui
        self.session = session
        self.browser = browser

        self.model = SearchModel(session)
        self.service = IrodsSearchService(session, app_name)

    # ---------------------------------------------------------
    # Initialization (called from Search.__init__)
    # ---------------------------------------------------------
    def init_search(self):
        self._connect_signals()
        self.ui.search_path_field.setText(self.session.home)
        self.ui.error_label.clear()
        self.ui.search_table.setRowCount(0)

    # ---------------------------------------------------------
    # Signal wiring
    # ---------------------------------------------------------
    def _connect_signals(self):
        self.ui.search_button.clicked.connect(self.on_search)
        self.ui.clear_button.clicked.connect(self.on_clear)
        self.ui.load_more_button.clicked.connect(self.on_load_more)
        self.ui.download_button.clicked.connect(self.on_download)
        self.ui.select_all_box.clicked.connect(self.on_select_all)
        self.ui.search_table.doubleClicked.connect(self.on_send_to_browser)

    # ---------------------------------------------------------
    # Search logic
    # ---------------------------------------------------------
    def on_search(self):
        # Extract raw values from UI
        meta_fields = [
            (self.ui.key1.text(), self.ui.val1.text(), self.ui.units1.text()),
            (self.ui.key2.text(), self.ui.val2.text(), self.ui.units2.text()),
            (self.ui.key3.text(), self.ui.val3.text(), self.ui.units3.text()),
            (self.ui.key4.text(), self.ui.val4.text(), self.ui.units4.text()),
        ]
   
        # Extract item types to search for
        checked = self.ui.radio_group.checkedButton()
        if "object" in checked.text().lower():
            item_type = "data_object"
        elif "collection" in checked.text().lower():
            item_type = "collection"
        else:
            item_type = None
        
        msg, params = self.model.validate(
            search_path=self.ui.search_path_field.text(),
            path_pattern=self.ui.path_pattern_field.text(),
            checksum=self.ui.checksum_field.text(),
            case_sensitive=self.ui.case_sensitive_box.isChecked(),
            item_type=item_type,
            meta_fields=meta_fields,
        )

        print(params)
    
        if msg:
            self.ui.error_label.setText(msg)
            return
    
        # Start search thread
        thread = self.service.start_search_thread(params)
        thread.result.connect(self._on_search_results)
        thread.finished.connect(lambda: self.ui.search_button.setEnabled(True))
    
        self.ui.search_button.setEnabled(False)
        self.ui.error_label.setText("Searching ...")
        thread.start()
    
    def _on_search_results(self, data):
        if "error" in data:
            self.ui.error_label.setText(data["error"])
            return
    
        results = data["results"]
        if not results:
            self.ui.error_label.setText("No objects or collections found.")
            return
    
        self.model.set_results(results)
        batch = self.model.next_batch()
        self.ui.search_table.setRowCount(0)
        self.ui.display_results(self._format_batch(batch))
    
        self.ui.error_label.setText("Search complete.")

    # ---------------------------------------------------------
    # Download logic
    # ---------------------------------------------------------
    def on_download(self):
        selected = self.ui.get_selected_paths()
        if not selected:
            self.ui.error_label.setText("No data selected.")
            return

        folder, overwrite = self.ui.ask_download_destination(selected)
        if folder is None:
            return

        irods_paths = [IrodsPath(self.session, p) for p in selected]
        thread = self.service.start_download_thread(irods_paths, folder, overwrite)

        thread.result.connect(self._on_download_finished)
        thread.current_progress.connect(self._on_download_progress)

        self.ui.error_label.setText("Downloading ...")
        thread.start()

    def _on_download_progress(self, state):
        _, _, done, total, failed = state
        self.ui.error_label.setText(f"{done} of {total} files; failed: {failed}.")

    def _on_download_finished(self, result):
        if result["error"]:
            self.ui.error_label.setText("Errors occurred during download.")
        else:
            self.ui.error_label.setText("Download finished.")

    # ---------------------------------------------------------
    # Table batching
    # ---------------------------------------------------------
    def on_load_more(self):
        batch = self.model.next_batch()
        self.ui.append_results(self._format_batch(batch))

    def _format_batch(self, batch):
        rows = []
        for ipath in batch:
            if ipath.dataobject_exists():
                rows.append((
                    "-d",
                    str(ipath),
                    ipath.size,
                    ipath.dataobject.create_time.strftime("%d-%m-%Y"),
                    ipath.dataobject.modify_time.strftime("%d-%m-%Y"),
                ))
            else:
                rows.append((
                    "-C",
                    str(ipath),
                    "",
                    ipath.collection.create_time.strftime("%d-%m-%Y"),
                    ipath.collection.modify_time.strftime("%d-%m-%Y"),
                ))
        return rows

    # ---------------------------------------------------------
    # Misc UI actions
    # ---------------------------------------------------------
    def on_clear(self):
        self.ui.search_table.setRowCount(0)
        self.ui.error_label.clear()

    def on_select_all(self):
        if self.ui.select_all_box.isChecked():
            for row in range(self.ui.search_table.rowCount()):
                self.ui.search_table.selectRow(row)
        else:
            self.ui.search_table.clearSelection()

    def on_send_to_browser(self):
        row = self.ui.search_table.currentIndex().row()
        path = self.ui.search_table.item(row, 1).text()
        ipath = IrodsPath(self.session, path)

        target = ipath if ipath.collection_exists() else ipath.parent
        self.browser.input_path.setText(str(target))
        self.browser.load_browser_table()
