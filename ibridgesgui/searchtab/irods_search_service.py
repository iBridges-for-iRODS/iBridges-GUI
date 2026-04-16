# irods_search_service.py
from pathlib import Path
from ibridges import download
from ibridgesgui.config import get_last_ienv_path, is_session_from_config
from ibridgesgui.gui_utils import combine_operations
from ibridgesgui.threads import SearchThread, TransferDataThread


class IrodsSearchService:
    def __init__(self, session, app_name):
        self.session = session
        import logging
        self.logger = logging.getLogger(app_name)

    def _env_path(self):
        if not is_session_from_config(self.session):
            raise RuntimeError("iBridges config changed during session.")
        return Path(get_last_ienv_path())

    def start_search_thread(self, params):
        env = self._env_path()
        return SearchThread(
            self.logger,
            env,
            params["search_path"],
            params["path_pattern"],
            params["meta_searches"],
            params["checksum"],
            params["case_sensitive"],
            params["item_type"],
        )

    def start_download_thread(self, irods_paths, folder, overwrite):
        env = self._env_path()
        ops = combine_operations([
            download(p, folder, overwrite=True, dry_run=True)
            for p in irods_paths
        ])
        return TransferDataThread(env, self.logger, ops, overwrite=overwrite)
