from manexp_web_lists.exceptions import PostgresqlConfigurationFailedError


def test_postgresql_configuration_failed_error() -> None:
    error = PostgresqlConfigurationFailedError(3)

    assert error.exit_code == 3
    assert str(error) == "PostgreSQL configuration failed with exit code 3"
