# search_controller.py

import logging
from ibridges import IrodsPath, download
from ibridges.executor import Operations
from ibridgesgui.threads import SearchThread, TransferDataThread
from ibridgesgui.gui_utils import prep_session_for_copy, combine_operations
from pathlib import Path
from .search_model import SearchModel
#from .irods_search_service import IrodsSearchService


class SearchController:
    """Controller for the Search tab."""

    def __init__(self, ui, session, app_name, browser):
        self.ui = ui
        self.session = session
        self.browser = browser
        self.logger = logging.getLogger(app_name)

        self.model = SearchModel(session)
        self.busy = False

    # ---------------------------------------------------------
    # Initialization (called from Search.__init__)
    # ---------------------------------------------------------
    def init_search(self):
        self._connect_signals()
        self.ui.search_path_field.setText(self.session.home)
        self.ui.error_label.clear()
        self.ui.search_table.setRowCount(0)
        self.ui.hide_result_elements()

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
        # Hide results elements in UI
        self.ui.hide_result_elements()
        if self.busy:
            print("busy")
            return
        self.busy = True
        self._set_busy(True)

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

    
        if msg:
            self.ui.error_label.setText(msg)
            return
        # Convert validated params into SearchThread arguments
        search_path = IrodsPath(self.session, params["search_path"])
        path_pattern = params["path_pattern"]
        checksum = params["checksum"]
        case_sensitive = params["case_sensitive"]
        item_type = params["item_type"]
        meta_searches = params["meta_searches"]
    
        # Create the thread directly
        env_path = prep_session_for_copy(self.session, self.ui.error_label)
        if env_path is None:
            return
        self.search_thread = SearchThread(
            logger=self.logger,
            ienv_path=env_path,
            search_path=search_path,
            path_pattern=path_pattern,
            meta_searches=meta_searches,
            checksum=checksum,
            case_sensitive=case_sensitive,
            item_type=item_type,
        ) 
   
        # Connect signals
        self.search_thread.result.connect(self._on_search_results)
        self.search_thread.finished.connect(self._on_search_finished)
    
        # Update UI
        self.ui.error_label.setText("Searching ...")
    
        # Start thread
        self.search_thread.start()

    def _on_search_results(self, data):
        self._search_results_data = data

    def _on_search_finished(self):
        self.busy = False
        self._set_busy(False)
        data = self._search_results_data
        self._search_results_data = None
        
        self.search_thread = None
        self.ui.search_button.setEnabled(True)
        self._set_busy(False)

        if "error" in data:
            self.ui.error_label.setText(data["error"])
            return
    
        results = data["results"]
        if not results:
            self.ui.error_label.setText("No objects or collections found.")
            return
        
        # Store all results in model
        self.model.set_results(results)

        # Show UI elements for results
        self.ui.show_result_elements()

        # Get first batch
        batch = self.model.next_batch()
        rows = self._format_batch(batch)

        self.ui.search_table.setRowCount(0)
        self.ui.display_results(self._format_batch(batch))
        self._update_load_more_visibility()
    
        self.ui.error_label.setText("Search complete.")


    # ---------------------------------------------------------
    # Download logic
    # ---------------------------------------------------------
    def on_download(self):
        if self.busy:
            return
        self.busy = True
        self._set_busy(True)
        
        self.ui.error_label.clear()
        self.ui.set_wait_cursor()
       
        # Retrieve selected paths (coll or obj)
        selected = self.ui.get_selected_paths()
        if not selected:
            self.ui.error_label.setText("No data selected.")
            self.ui.set_normal_cursor()
            return

        # Determine download destination
        folder, overwrite = self.ui.ask_download_destination(selected)
        if folder is None:
            self.ui.set_normal_cursor()
            return
        if not overwrite:
            return

        # Convert UI strings to iRODS paths
        irods_paths = [IrodsPath(self.session, p) for p in selected]

        # Combine several downloads in one ibridges operations object
        ops = combine_operations([
            download(p, folder, overwrite=True, dry_run=True)
            for p in irods_paths
        ])

        # Start download
        env_path = prep_session_for_copy(self.session, self.ui.error_label)
        if env_path is None:
            self.ui.error_label.setText("No donwload. Cannot create new irods session.")
            return

        self.download_thread=TransferDataThread(
            ienv_path=env_path,
            logger=self.logger,
            ops=ops,
            overwrite=overwrite
        )
        self.download_thread.result.connect(self._on_download_finished)
        self.download_thread.finished.connect(self._on_download_finished_cleanup)
        self.download_thread.current_progress.connect(self._on_download_progress)

        
        self.ui.error_label.setText("Downloading ...")
        self.download_thread.start()

    def _on_download_progress(self, state):
        _, _, done, total, failed, _ = state
        self.ui.error_label.setText(f"{done} of {total} files; failed: {failed}.")


    def _on_download_finished(self, data):
        self._download_result = data

    def _on_download_finished_cleanup(self):
        self.busy = False
        self._set_busy(False)
        self.ui.set_normal_cursor()
        
        data = self._download_result
        self._download_result = None
        
        self.download_thread = None
        self.ui.set_normal_cursor()
        self._set_busy(False)
        
        if "error" in data:
            self.ui.error_label.setText(data["error"])
        else:
            self.ui.error_label.setText("Download complete.")

    # ---------------------------------------------------------
    # Table batching
    # ---------------------------------------------------------
    def on_load_more(self):
        batch = self.model.next_batch()
        rows = self._format_batch(batch)
    
        self.ui.append_results(rows)
        self._update_load_more_visibility()
    
    def _update_load_more_visibility(self, batch_size=25):
        total = len(self.model.results)
        loaded_batches = self.model.current_batch  # incremented by next_batch()
    
        if total > batch_size * loaded_batches:
            self.ui.load_more_button.show()
            remaining = total - batch_size * loaded_batches
            self.ui.load_more_button.setText(
                f"Load next {min(batch_size, remaining)} of {total} results."
            )
        else:
            self.ui.load_more_button.hide()
    


    def _format_batch(self, batch):
        rows = []
        for path in batch:
            ipath = IrodsPath(self.session, path) 
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

    def _set_busy(self, busy: bool):
        self.ui.search_button.setEnabled(not busy)
        self.ui.download_button.setEnabled(not busy)
        self.ui.clear_button.setEnabled(not busy)
        self.ui.load_more_button.setEnabled(not busy)

