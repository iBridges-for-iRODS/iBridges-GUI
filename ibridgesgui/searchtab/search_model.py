"""Search model."""
from ibridges import IrodsPath
from ibridges.search import MetaSearch


class SearchModel:
    """Model for search view."""

    def __init__(self, session):
        """Init."""
        self.session = session
        self.results = []
        self.current_batch = 0

    def validate(
        self,
        search_path: str,
        path_pattern: str,
        checksum: str,
        case_sensitive: bool,
        item_type: str,
        meta_fields: list[tuple[str, str, str]],
    ):
        """Validate raw search parameters (no UI dependency).

        Returns
        -------
            (msg, params_dict)

        """
        # Convert to IrodsPath
        search_path_obj = IrodsPath(self.session, search_path)

        # Build MetaSearch objects
        meta_searches = []
        for key, value, units in meta_fields:
            if key or value or units:
                meta_searches.append(
                    MetaSearch(key or "%", value or "%", units or "%")
                )

        # Validation
        if not search_path_obj.collection_exists():
            msg = f"Search in {search_path_obj}: Collection does not exist."
            return msg, None

        if not meta_searches and not path_pattern and not checksum:
            msg = "Please provide some search criteria."
            return msg, None

        # Pack into dict for controller + service
        params = {
            "search_path": search_path_obj,
            "path_pattern": path_pattern or None,
            "meta_searches": meta_searches,
            "checksum": checksum or None,
            "case_sensitive": case_sensitive,
            "item_type": item_type,
        }

        return None, params

    # ---------------- RESULTS ---------------- #

    def set_results(self, results):
        """Cache all results from search."""
        self.results = results
        self.current_batch = 0

    def next_batch(self, batch_size=25):
        """Get next batch of results."""
        start = self.current_batch * batch_size
        end = start + batch_size
        self.current_batch += 1
        return self.results[start:end]
