import pytest
from unittest.mock import MagicMock
from pathlib import Path

from ibridgesgui.login import LoginDialog


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_envs(tmp_path):
    """Fake environments returned by load_envs_from_cli_and_fs()."""
    env1 = tmp_path / "env1.json"
    env2 = tmp_path / "env2.json"
    env1.write_text("{}")
    env2.write_text("{}")

    return {
        "alias1": (env1, {"irodsa_backup": "cachedpw"}),
        "alias2": (env2, {}),  # no cached password
    }


@pytest.fixture
def fake_session_manager():
    """Mock session manager with check_home and check_resource."""
    sm = MagicMock()
    sm.check_home.return_value = True
    sm.check_resource.return_value = True
    sm.config_manager.save_current_settings = MagicMock()
    sm.config_manager.set_last_ienv = MagicMock()
    return sm


@pytest.fixture
def patched_login(monkeypatch, qtbot, fake_envs, fake_session_manager):
    """Create a LoginDialog with all external dependencies mocked."""

    # Patch load_envs_from_cli_and_fs
    monkeypatch.setattr(
        "ibridgesgui.login.load_envs_from_cli_and_fs",
        lambda _: fake_envs.copy()
    )

    # Patch get_last_ienv_name
    monkeypatch.setattr(
        "ibridgesgui.login.get_last_ienv_name",
        lambda: None
    )

    # Patch check_irods_config
    monkeypatch.setattr(
        "ibridgesgui.login.check_irods_config",
        lambda *a, **k: "All checks passed successfully."
    )

    monkeypatch.setattr(
        "ibridgesgui.login.LoginDialog.strictwrite",
        lambda *a, **k: 1
    )

    # Patch Session
    class FakeSession:
        def __init__(self, irods_env=None, password=None):
            self.irods_env = Path(irods_env)
            self.password = password
            self.username = "user"
            self.host = "host"
            self.home = "/zone/home/user"
            self.default_resc = "resc"

        def write_pam_password(self):
            pass

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg = LoginDialog(parent=None, logger=MagicMock(), session_manager=fake_session_manager)
    qtbot.addWidget(dlg)
    return dlg, fake_session_manager


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_init_envbox(patched_login, fake_envs):
    dlg, _ = patched_login
    items = [dlg.envbox.itemText(i) for i in range(dlg.envbox.count())]

    assert any("alias1" in item for item in items)
    assert any("alias2" in item for item in items)


def test_init_password_cached(patched_login, fake_envs):
    dlg, _ = patched_login

    # Select alias1 (cached password)
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    assert dlg._init_password() is True
    assert dlg.password_field.text() == "***********"


def test_init_password_uncached(patched_login, fake_envs):
    dlg, _ = patched_login

    dlg.envbox.setCurrentText(f"alias2 - {fake_envs['alias2'][0]}")
    assert dlg._init_password() is False
    assert dlg.password_field.text() == ""


def test_parse_envbox_text(patched_login, fake_envs):
    dlg, _ = patched_login

    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    alias, path = dlg._parse_envbox_text()

    assert alias == "alias1"
    assert path == fake_envs["alias1"][0]


def test_resolve_password_cached(patched_login, fake_envs):
    dlg, _ = patched_login
    entry = fake_envs["alias1"][1]

    pw = dlg._resolve_password(entry, "***********")
    assert pw == "cachedpw"


def test_resolve_password_typed(patched_login):
    dlg, _ = patched_login
    entry = {}

    pw = dlg._resolve_password(entry, "mypw")
    assert pw == "mypw"


def test_resolve_password_missing(patched_login):
    dlg, _ = patched_login
    entry = {}

    pw = dlg._resolve_password(entry, "")
    assert pw is None
    assert "Password required" in dlg.error_label.text()


def test_validate_env_config_ok(patched_login, fake_envs):
    dlg, _ = patched_login
    assert dlg._validate_env_config(fake_envs["alias1"][0]) is True


def test_validate_env_config_bad(patched_login, monkeypatch, fake_envs):
    dlg, _ = patched_login

    monkeypatch.setattr(
        "ibridgesgui.login.check_irods_config",
        lambda *a, **k: "Bad config"
    )

    assert dlg._validate_env_config(fake_envs["alias1"][0]) is False
    assert "Go to menu Configure" in dlg.error_label.text()


def test_login_success_cached_password(patched_login, fake_envs):
    dlg, sm = patched_login

    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("***********")

    dlg._on_connect()

    assert dlg.accepted_credentials is not None
    assert dlg.accepted_credentials["alias"] == "alias1"
    assert dlg.accepted_credentials["env_path"] == fake_envs["alias1"][0]


def test_login_success_typed_password(patched_login, fake_envs):
    dlg, sm = patched_login

    dlg.envbox.setCurrentText(f"alias2 - {fake_envs['alias2'][0]}")
    dlg.password_field.setText("mypw")

    dlg._on_connect()

    assert dlg.accepted_credentials is not None
    assert dlg.accepted_credentials["session"].password == "mypw"


def test_login_home_invalid(patched_login, fake_envs):
    dlg, sm = patched_login

    sm.check_home.return_value = False

    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("***********")

    dlg._on_connect()

    assert '"irods_home"' in dlg.error_label.text()
    assert dlg.accepted_credentials is None


def test_login_resource_invalid(patched_login, fake_envs):
    dlg, sm = patched_login

    sm.check_resource.return_value = False

    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("***********")

    dlg._on_connect()

    assert "not writeable" in dlg.error_label.text()
    assert dlg.accepted_credentials is None


def test_login_password_error(patched_login, monkeypatch, fake_envs):
    from ibridges.session import PasswordError

    class FakeSession:
        def __init__(self, *a, **k):
            raise PasswordError("wrong")

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg, _ = patched_login
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("pw")

    dlg._on_connect()

    assert "Wrong password" in dlg.error_label.text()


def test_login_login_error(patched_login, monkeypatch, fake_envs):
    from ibridges.session import LoginError

    class FakeSession:
        def __init__(self, *a, **k):
            raise LoginError("bad")

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg, _ = patched_login
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("pw")

    dlg._on_connect()

    assert "not setup correctly" in dlg.error_label.text()


def test_login_connection_error(patched_login, monkeypatch, fake_envs):
    class FakeSession:
        def __init__(self, *a, **k):
            raise ConnectionError("net")

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg, _ = patched_login
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("pw")

    dlg._on_connect()

    assert "Cannot connect" in dlg.error_label.text()


def test_login_resource_missing(patched_login, monkeypatch, fake_envs):
    from irods.exception import ResourceDoesNotExist

    class FakeSession:
        def __init__(self, *a, **k):
            raise ResourceDoesNotExist("missing")

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg, _ = patched_login
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("pw")

    dlg._on_connect()

    assert "does not exist" in dlg.error_label.text()


def test_login_generic_exception(patched_login, monkeypatch, fake_envs):
    class FakeSession:
        def __init__(self, *a, **k):
            raise RuntimeError("boom")

    monkeypatch.setattr("ibridgesgui.login.Session", FakeSession)

    dlg, _ = patched_login
    dlg.envbox.setCurrentText(f"alias1 - {fake_envs['alias1'][0]}")
    dlg.password_field.setText("pw")

    dlg._on_connect()

    assert "Login failed" in dlg.error_label.text()

