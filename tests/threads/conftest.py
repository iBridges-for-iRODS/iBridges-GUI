# tests/threads/conftest.py

import pytest
from unittest.mock import Mock


# ---------------------------------------------------------------------------
# Fake session
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_session():
    """A fake iRODS session object with the attributes the threads expect."""
    session = Mock()

    # Real threads expect session.irods_session
    inner = Mock()
    inner.data_objects = Mock()
    inner.collections = Mock()

    session.irods_session = inner
    return session


# ---------------------------------------------------------------------------
# Patch Session.close() globally
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_session_close(monkeypatch):
    """Patch Session.close() before Session is replaced."""
    def fake_close(self):
        self.irods_session = None

    monkeypatch.setattr(
        "ibridgesgui.threads.Session.close",
        fake_close,
        raising=False,
    )


# ---------------------------------------------------------------------------
# Patch Session(...) constructor
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_session_ctor(monkeypatch, fake_session):
    """Patch Session(...) to always return fake_session."""
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: fake_session,
        raising=False,
    )
    return fake_session


# ---------------------------------------------------------------------------
# Fake IrodsPath factory
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_ipath():
    def _make(path: str):
        obj = Mock()
        obj.path = path
        obj.name = path.split("/")[-1]
        obj.size = 5
        obj.__str__ = lambda self=obj: path
        return obj
    return _make


# ---------------------------------------------------------------------------
# Fake logger
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_logger():
    """A logger mock for all threads."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger

