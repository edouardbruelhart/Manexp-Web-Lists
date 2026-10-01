from pathlib import Path

import pyarrow.parquet as pq

from manexp_web_lists.exceptions import UnresolvedForeignKeyError


def generate_foreign_key_constraints(
    files: dict[str, Path],
) -> list[str]:
    """
    Generate foreign key constraints for a list of Parquet files.

    Args:
        files: a dictionary where the keys are table names and the values are Path objects to Parquet files.

    Returns:
        list[str]: a list of foreign key constraints.

    Raises:
        UnresolvedForeignKeyError: Raised when an unsupported foreign key is encountered.

    Returns:
        list[str]: a list of foreign key constraints.
    """

    foreign_keys = []

    table_names = set(files)

    for table_name, file in files.items():
        schema = pq.read_schema(file)

        for field in schema:
            target = foreign_key_target(
                table_name,
                field.name,
            )

            if target is None:
                continue

            target_table, target_column = target

            if target_table not in table_names:
                raise UnresolvedForeignKeyError(table_name, field.name, target_table, target_column)

            constraint_name = f"fk_{table_name}_{field.name.removesuffix('_id')}"

            foreign_keys.append(
                "DO $$\n"
                "BEGIN\n"
                "   IF NOT EXISTS (\n"
                "       SELECT 1\n"
                "       FROM pg_constraint\n"
                f"       WHERE pg_constraint.conname = '{constraint_name}'\n"
                "   ) THEN\n"
                f'       ALTER TABLE "{table_name}"\n'
                f'       ADD CONSTRAINT "{constraint_name}"\n'
                f'       FOREIGN KEY ("{field.name}")\n'
                f'       REFERENCES "{target_table}" ("{target_column}");\n'
                "   END IF;\n"
                "END\n"
                "$$;"
            )

    return foreign_keys


def foreign_key_target(
    table_name: str,
    column_name: str,
) -> tuple[str, str] | None:
    """
    Get the target for a foreign key constraint.

    Args:
        table_name: the name of the table where the foreign key constraint is located.
        column_name: the name of the column where the foreign key constraint is located.

    Returns:
        tuple[str, str] | None: a tuple containing the target table name and the target column name. If no target is found, returns None.
    """

    if column_name == "parent_id":
        return table_name, "id"

    if not column_name.endswith("_id"):
        return None

    prefix = column_name.removesuffix("_id")

    return prefix, "id"
