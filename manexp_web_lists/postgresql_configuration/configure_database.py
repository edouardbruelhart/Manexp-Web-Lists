import os
import platform
import subprocess
from pathlib import Path

from manexp_web_lists.exceptions import InvalidEnvironmentError, PostgresqlConfigurationFailedError, UnsupportedOSError


def configure_database() -> None:
    """
    Configure Docker and PostgreSQL instances to then store the generated tables.

    Raises:
        InvalidEnvironmentError: Raised when environment variables are not set or bad
        UnsupportedOSError: Raised when automatic setup is enabled on an unsupported operating system
        PostgresqlConfigurationFailedError: Raised when the automatic setup encounters an error
    """

    # Get environment variables
    automatic_configuration = os.getenv("AUTOMATIC_DB_SETUP")

    # Check that variables ar correct
    if automatic_configuration not in ("0", "1"):
        raise InvalidEnvironmentError

    # Exit configuration if configuration is disabled
    if automatic_configuration == "0":
        return

    # Check that operating system is supported
    if platform.system() != "Linux":
        raise UnsupportedOSError(platform.system())

    # Run configuration script
    script = Path(__file__).resolve().parents[0] / "scripts" / "configure_database.sh"

    try:
        subprocess.run(  # noqa: S603 — script is a fixed file bundled with the package
            ["/bin/bash", str(script)],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise PostgresqlConfigurationFailedError(exc.returncode) from exc
