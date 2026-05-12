from pathlib import Path
from unittest.mock import Mock
from irods.exception import CAT_NO_ACCESS_PERMISSION
import errno
from ibridgesgui.threads import SyncThread


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_thread(fake_logger, dry_run=False):
    """Create a SyncThread with minimal boilerplate."""
    return SyncThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        source="irods:/tempZone/home",
        target="/local/path",
        dry_run=dry_run,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_sync_thread_success(
    qtbot, monkeypatch, mock_session_ctor, patch_session_close, fake_logger
):
    monkeypatch.setattr(
        "ibridgesgui.threads.sync",
        lambda *a, **k: {"dry_run": True},
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )

    thread = make_thread(fake_logger, dry_run=True)

    with qtbot.waitSignal(thread.result, timeout=1000) as blocker:
        thread.run()

    assert blocker.args == [{"error": "", "result": {"dry_run": True}}]


def test_sync_thread_permission_error(
    qtbot, monkeypatch, mock_session_ctor, fake_logger
):
    def raise_perm(*a, **k):
        raise PermissionError(errno.EACCES, "no access", "/restricted")

    monkeypatch.setattr("ibridgesgui.threads.sync", raise_perm)
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )

    thread = make_thread(fake_logger)

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "No access" in blocker.args[0]["error"]


def test_sync_thread_generic_error(
    qtbot, monkeypatch, mock_session_ctor, fake_logger
):
    monkeypatch.setattr(
        "ibridgesgui.threads.sync",
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

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "boom" in blocker.args[0]["error"]

