from pathlib import Path
from unittest.mock import Mock
from ibridgesgui.threads import SearchThread
from irods.exception import NetworkException

def test_search_thread_success(qtbot, monkeypatch, mock_session_ctor, patch_session_close, fake_ipath, fake_logger):
    fake_results = [fake_ipath("/a/b/c1"), fake_ipath("/a/b/c2")]

    monkeypatch.setattr("ibridgesgui.threads.search_data", lambda *a, **k: fake_results)

    thread = SearchThread(
        logger=fake_logger,
        ienv_path=Path("/fake/env"),
        search_path=Mock(),
        path_pattern="*.txt",
        meta_searches=[],
        checksum="",
        case_sensitive=False,
        item_type="data_object",
    )

    with qtbot.waitSignal(thread.result, timeout=1000) as blocker:
        thread.run()

    assert blocker.args == [{"results": ["/a/b/c1", "/a/b/c2"]}]


def test_search_thread_network_error(qtbot, monkeypatch, mock_session_ctor, fake_logger):
    monkeypatch.setattr(
        "ibridgesgui.threads.search_data",
        lambda *a, **k: (_ for _ in ()).throw(NetworkException())
    )

    thread = SearchThread(
        logger=fake_logger,
        ienv_path=Path("/fake/env"),
        search_path=Mock(),
        path_pattern="*.txt",
        meta_searches=[],
        checksum="",
        case_sensitive=False,
        item_type="data_object",
    )

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "takes too long" in blocker.args[0]["error"]

def test_search_thread_unexpected_error(qtbot, monkeypatch, mock_session_ctor, fake_logger):
    monkeypatch.setattr(
        "ibridgesgui.threads.search_data",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    )

    thread = SearchThread(
        logger=fake_logger,
        ienv_path=Path("/fake/env"),
        search_path=Mock(),
        path_pattern="*.txt",
        meta_searches=[],
        checksum="",
        case_sensitive=False,
        item_type="data_object",
    )

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "Unexpected error" in blocker.args[0]["error"]

