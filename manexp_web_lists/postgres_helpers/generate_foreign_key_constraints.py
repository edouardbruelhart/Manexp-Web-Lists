from pathlib import Path

import pyarrow.parquet as pq
from psycopg import sql

from manexp_web_lists.exceptions import UnresolvedForeignKeyError


def generate_foreign_key_constraints(
    files: dict[str, Path],
) -> list[sql.Composed]:
    """
    Generate foreign key constraints for a list of Parquet files.

    Args:
        files: A dictionary where keys are table names and values are Path objects to Parquet files.

    Returns:
        list[sql.Composed]: A list of SQL Composed objects representing foreign key constraints.

    Raises:
        UnresolvedForeignKeyError: Raised when a foreign key constraint cannot be resolved.
    """

    foreign_keys: list[sql.Composed] = []
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
                raise UnresolvedForeignKeyError(
                    table_name,
                    field.name,
                    target_table,
                    target_column,
                )

            constraint_name = f"fk_{table_name}_{field.name.removesuffix('_id')}"

            foreign_keys.append(
                sql.SQL(
                    """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1
                            FROM pg_constraint
                            WHERE pg_constraint.conname = {constraint_name_value}
                        ) THEN
                            ALTER TABLE {table_name}
                            ADD CONSTRAINT {constraint_name_identifier}
                            FOREIGN KEY ({field_name})
                            REFERENCES {target_table} ({target_column});
                        END IF;
                    END
                    $$;
                    """
                ).format(
                    constraint_name_value=sql.Literal(constraint_name),
                    constraint_name_identifier=sql.Identifier(constraint_name),
                    table_name=sql.Identifier(table_name),
                    field_name=sql.Identifier(field.name),
                    target_table=sql.Identifier(target_table),
                    target_column=sql.Identifier(target_column),
                )
            )

            # Add an index for this foreign key.
            index_name = f"idx_{table_name}_{field.name}"

            foreign_keys.append(
                sql.SQL(
                    """
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {table_name} ({field_name});
                    """
                ).format(
                    index_name=sql.Identifier(index_name),
                    table_name=sql.Identifier(table_name),
                    field_name=sql.Identifier(field.name),
                )
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

    if column_name == "taxon_id":
        return prefix, "upov_code"

    return prefix, "id"
