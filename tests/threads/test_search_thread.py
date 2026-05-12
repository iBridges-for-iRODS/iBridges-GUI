from pathlib import Path
from unittest.mock import Mock
from irods.exception import NetworkException
from ibridgesgui.threads import SearchThread


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_thread(fake_logger):
    """Create a SearchThread with minimal boilerplate."""
    return SearchThread(
        logger=fake_logger,
        ienv_path=Path("/fake/env"),
        search_path=Mock(),
        path_pattern="*.txt",
        meta_searches=[],
        checksum="",
        case_sensitive=False,
        item_type="data_object",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_search_thread_success(
    qtbot, monkeypatch, mock_session_ctor, fake_ipath, fake_logger
):
    fake_results = [fake_ipath("/a/b/c1"), fake_ipath("/a/b/c2")]

    monkeypatch.setattr(
        "ibridgesgui.threads.search_data",
        lambda *a, **k: fake_results,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )

    thread = make_thread(fake_logger)

    with qtbot.waitSignal(thread.result, timeout=1000) as blocker:
        thread.run()

    assert blocker.args == [{"results": ["/a/b/c1", "/a/b/c2"]}]


def test_search_thread_network_error(
    qtbot, monkeypatch, mock_session_ctor, fake_logger
):
    monkeypatch.setattr(
        "ibridgesgui.threads.search_data",
        lambda *a, **k: (_ for _ in ()).throw(NetworkException()),
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )

    thread = make_thread(fake_logger)
    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "takes too long" in blocker.args[0]["error"]


def test_search_thread_unexpected_error(
    qtbot, monkeypatch, mock_session_ctor, fake_logger
):
    monkeypatch.setattr(
        "ibridgesgui.threads.search_data",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )

    thread = make_thread(fake_logger)
    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "Unexpected error" in blocker.args[0]["error"]

