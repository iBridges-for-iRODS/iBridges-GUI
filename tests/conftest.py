# tests/conftest.py

import pytest
from ibridges import IrodsPath


class DummyCollections:
    def exists(self, path: str) -> bool:
        return True   # pretend all collections exist


class DummyIrodsSession:
    def __init__(self):
        self.collections = DummyCollections()


class DummySession:
    def __init__(self):
        self.irods_session = DummyIrodsSession()


def make_path(path: str) -> IrodsPath:
    return IrodsPath(DummySession(), path)


@pytest.fixture
def make_irods_path():
    return make_path

