# tests/threads/conftest.py

import pytest
from unittest.mock import Mock


@pytest.fixture
def fake_session():
    """A fake iRODS session object with the attributes the threads expect."""
    session = Mock()
    session.irods_session = object()
    return session


@pytest.fixture(autouse=True)
def patch_session_close(monkeypatch):
    """Patch Session.close() before Session is replaced."""
    def fake_close(self):
        self.irods_session = None

    monkeypatch.setattr(
        "ibridgesgui.threads.Session.close",
        fake_close,
        raising=False,  # important: allows patching even if Session is later replaced
    )


@pytest.fixture
def mock_session_ctor(monkeypatch, fake_session):
    """Patch Session(...) to always return fake_session."""
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: fake_session,
        raising=False,
    )
    return fake_session


@pytest.fixture
def fake_ipath():
    """Return a function that creates a fake IrodsPath-like object."""
    def _make(path: str):
        obj = Mock()
        obj.__str__ = lambda self=obj: path
        obj.size = 5
        return obj
    return _make


@pytest.fixture
def fake_logger():
    """A logger mock for all threads."""
    return Mock()

