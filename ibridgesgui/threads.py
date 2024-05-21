"""Thread classes for length iBridges functions."""
from ibridges import search_data
from irods.exception import NetworkException
from PyQt6.QtCore import QThread, pyqtSignal


class SearchThread(QThread):
    """Start iRODS search in an own thread using the same iRODS session."""

    succeeded = pyqtSignal(dict)

    def __init__(self, session, path, checksum, key_vals):
        """Pass searh parameters."""
        super().__init__()
        self.session = session
        self.path = path
        self.checksum = checksum
        self.key_vals = key_vals

    def run(self):
        """Run the thread."""
        search_out = {}
        try:
            search_out['results'] = search_data(self.session, path=self.path,
                                       checksum=self.checksum, key_vals=self.key_vals)
        except NetworkException:
            search_out['error'] = "Search takes too long. Please provide more parameters."
        self.succeeded.emit(search_out)
