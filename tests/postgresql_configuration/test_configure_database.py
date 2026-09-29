import subprocess
from unittest.mock import patch

import pytest

from manexp_web_lists.exceptions import (
    InvalidEnvironmentError,
    PostgresqlConfigurationFailedError,
    UnsupportedOSError,
)
from manexp_web_lists.postgresql_configuration import configure_database


def test_configure_database_returns_when_automatic_setup_is_disabled(
    monkeypatch,
):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", "0")

    with patch("manexp_web_lists.postgresql_configuration.configure_database.subprocess.run") as run:
        configure_database()

    run.assert_not_called()


def test_configure_database_raises_when_automatic_setup_is_invalid(
    monkeypatch,
):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", "invalid")

    with pytest.raises(InvalidEnvironmentError):
        configure_database()


@pytest.mark.parametrize("value", ["", "2", "true", "false", "yes", "no"])
def test_configure_database_raises_when_automatic_setup_is_not_0_or_1(
    monkeypatch,
    value,
):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", value)

    with pytest.raises(InvalidEnvironmentError):
        configure_database()


def test_configure_database_raises_on_unsupported_os(monkeypatch):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", "1")

    with (
        patch("manexp_web_lists.postgresql_configuration.configure_database.platform.system", return_value="Windows"),
        pytest.raises(UnsupportedOSError),
    ):
        configure_database()


def test_configure_database_runs_script_on_linux(monkeypatch):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", "1")

    with (
        patch("manexp_web_lists.postgresql_configuration.configure_database.subprocess.run") as run,
        patch("manexp_web_lists.postgresql_configuration.configure_database.platform.system", return_value="Linux"),
    ):
        configure_database()

    run.assert_called_once_with(
        ["/bin/bash", pytest.approx(run.call_args.args[0][1])],
        check=True,
    )


def test_configure_database_raises_when_script_fails(monkeypatch):
    monkeypatch.setenv("AUTOMATIC_DB_SETUP", "1")

    error = subprocess.CalledProcessError(returncode=42, cmd="configure_database.sh")

    with (
        patch("manexp_web_lists.postgresql_configuration.configure_database.subprocess.run", side_effect=error),
        patch("manexp_web_lists.postgresql_configuration.configure_database.platform.system", return_value="Linux"),
        pytest.raises(PostgresqlConfigurationFailedError),
    ):
        configure_database()
