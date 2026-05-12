from pathlib import Path
from unittest.mock import Mock
from ibridgesgui.threads import TransferDataThread


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_valid_session(monkeypatch):
    """Ensure BaseIrodsThread accepts the session."""
    monkeypatch.setattr(
        "ibridgesgui.threads.is_session_from_config",
        lambda *_: True,
    )
    monkeypatch.setattr(
        "ibridgesgui.threads.Session",
        lambda *a, **k: Mock(close=lambda: None),
    )


def make_ops(upload=None, download=None, meta_download=None, meta_upload=None):
    """Create a fully-populated ops mock with sensible defaults."""
    ops = Mock()
    ops.upload = upload or []
    ops.download = download or []
    ops.options = {}
    ops.resc_name = None

    ops.execute_create_coll = Mock()
    ops.execute_create_dir = Mock()

    ops.execute_meta_download = Mock() if meta_download is None else meta_download
    ops.execute_meta_upload = Mock() if meta_upload is None else meta_upload

    return ops


def make_thread(fake_logger, ops):
    """Create a TransferDataThread with minimal boilerplate."""
    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )
    thread.invalid_session = False
    return thread


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_transfer_thread_success(qtbot, monkeypatch, mock_session_ctor, patch_session_close, fake_logger, tmp_path):
    make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")

    irods_path = Mock(size=5)

    ops = make_ops(
        upload=[(local_file, irods_path)],
        download=[(irods_path, local_file)],
    )

    monkeypatch.setattr("ibridgesgui.threads._obj_put", lambda *a, **k: None)
    monkeypatch.setattr("ibridgesgui.threads._obj_get", lambda *a, **k: None)

    thread = make_thread(fake_logger, ops)

    with qtbot.waitSignal(thread.result, timeout=1000) as blocker:
        thread.run()

    assert blocker.args == [{"error": ""}]
    ops.execute_meta_download.assert_called_once()


def test_transfer_thread_upload_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")
    irods_path = Mock(size=5)

    ops = make_ops(upload=[(local_file, irods_path)])

    monkeypatch.setattr(
        "ibridgesgui.threads._obj_put",
        lambda *a, **k: (_ for _ in ()).throw(Exception("upload failed")),
    )

    thread = make_thread(fake_logger, ops)

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "upload failed" in blocker.args[0]["error"]


def test_transfer_thread_download_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")
    irods_path = Mock(size=5)

    ops = make_ops(download=[(irods_path, local_file)])

    monkeypatch.setattr(
        "ibridgesgui.threads._obj_get",
        lambda *a, **k: (_ for _ in ()).throw(Exception("download failed")),
    )

    thread = make_thread(fake_logger, ops)

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "download failed" in blocker.args[0]["error"]


def test_transfer_thread_metadata_download_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger):
    make_valid_session(monkeypatch)

    ops = make_ops(meta_download=Mock(side_effect=Exception("meta-down")))

    thread = make_thread(fake_logger, ops)

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "meta-down" in blocker.args[0]["error"]


def test_transfer_thread_metadata_upload_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger):
    """
    TransferDataThread NEVER calls execute_meta_upload().
    So even if it raises, the error must NOT appear.
    """
    make_valid_session(monkeypatch)

    ops = make_ops(meta_upload=Mock(side_effect=Exception("meta-up")))

    thread = make_thread(fake_logger, ops)

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    # Since execute_meta_upload is never called, no error should appear.
    assert blocker.args == [{"error": ""}]

