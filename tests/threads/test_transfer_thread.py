from pathlib import Path
from unittest.mock import Mock
from ibridgesgui.threads import TransferDataThread


def _make_valid_session(monkeypatch):
    """Patch Session + session validation so BaseIrodsThread never rejects."""
    monkeypatch.setattr("ibridgesgui.threads.is_session_from_config", lambda *_: True)

    class FakeSession:
        def close(self): 
            pass

    monkeypatch.setattr("ibridgesgui.threads.Session", lambda *a, **k: FakeSession())


def test_transfer_thread_success(qtbot, monkeypatch, mock_session_ctor, patch_session_close, fake_logger, tmp_path):
    _make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")

    irods_path = Mock()
    irods_path.size = 5

    ops = Mock()
    ops.upload = [(local_file, irods_path)]
    ops.download = [(irods_path, local_file)]
    ops.options = {}
    ops.resc_name = None

    # These must accept any args
    ops.execute_create_coll = Mock(side_effect=lambda *a, **k: None)
    ops.execute_create_dir = Mock(side_effect=lambda *a, **k: None)

    # Only metadata DOWNLOAD exists in your real thread
    ops.execute_meta_download = Mock()

    # No metadata upload in your real code → remove expectation
    ops.execute_meta_upload = Mock()

    monkeypatch.setattr("ibridgesgui.threads._obj_put", lambda *a, **k: None)
    monkeypatch.setattr("ibridgesgui.threads._obj_get", lambda *a, **k: None)

    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )

    thread.invalid_session = False

    with qtbot.waitSignal(thread.result, timeout=1000) as blocker:
        thread.run()

    assert blocker.args == [{"error": ""}]
    ops.execute_meta_download.assert_called_once()


def test_transfer_thread_upload_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    _make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")

    irods_path = Mock()
    irods_path.size = 5

    ops = Mock()
    ops.upload = [(local_file, irods_path)]
    ops.download = []
    ops.options = {}
    ops.resc_name = None
    ops.execute_create_coll = Mock(side_effect=lambda *a, **k: None)
    ops.execute_create_dir = Mock(side_effect=lambda *a, **k: None)
    ops.execute_meta_download = Mock()

    monkeypatch.setattr(
        "ibridgesgui.threads._obj_put",
        lambda *a, **k: (_ for _ in ()).throw(Exception("upload failed"))
    )

    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )

    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "upload failed" in blocker.args[0]["error"]


def test_transfer_thread_download_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    _make_valid_session(monkeypatch)

    local_file = tmp_path / "file.txt"
    local_file.write_text("hello")

    irods_path = Mock()
    irods_path.size = 5

    ops = Mock()
    ops.upload = []
    ops.download = [(irods_path, local_file)]
    ops.options = {}
    ops.resc_name = None
    ops.execute_create_coll = Mock(side_effect=lambda *a, **k: None)
    ops.execute_create_dir = Mock(side_effect=lambda *a, **k: None)
    ops.execute_meta_download = Mock()

    monkeypatch.setattr(
        "ibridgesgui.threads._obj_get",
        lambda *a, **k: (_ for _ in ()).throw(Exception("download failed"))
    )

    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )

    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "download failed" in blocker.args[0]["error"]


def test_transfer_thread_metadata_download_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    _make_valid_session(monkeypatch)

    ops = Mock()
    ops.upload = []
    ops.download = []
    ops.options = {}
    ops.resc_name = None
    ops.execute_create_coll = Mock(side_effect=lambda *a, **k: None)
    ops.execute_create_dir = Mock(side_effect=lambda *a, **k: None)
    ops.execute_meta_download = Mock(side_effect=Exception("meta-down"))

    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )

    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    assert "meta-down" in blocker.args[0]["error"]


def test_transfer_thread_metadata_upload_failure(qtbot, monkeypatch, mock_session_ctor, fake_logger, tmp_path):
    """
    Your real TransferDataThread does NOT call execute_meta_upload().
    So this test must assert that metadata upload errors do NOT appear.
    """
    _make_valid_session(monkeypatch)

    ops = Mock()
    ops.upload = []
    ops.download = []
    ops.options = {}
    ops.resc_name = None
    ops.execute_create_coll = Mock(side_effect=lambda *a, **k: None)
    ops.execute_create_dir = Mock(side_effect=lambda *a, **k: None)
    ops.execute_meta_download = Mock()
    ops.execute_meta_upload = Mock(side_effect=Exception("meta-up"))

    thread = TransferDataThread(
        ienv_path=Path("/fake/env"),
        logger=fake_logger,
        ops=ops,
        overwrite=True,
    )

    thread.invalid_session = False

    with qtbot.waitSignal(thread.result) as blocker:
        thread.run()

    # Since execute_meta_upload is NEVER called in your real code,
    # its exception should never appear.
    assert blocker.args == [{"error": ""}]

