from manexp_web_lists.exceptions import UnresolvedForeignKeyError


def test_unresolved_foreign_key_error() -> None:
    error = UnresolvedForeignKeyError("culture", "culture_additional_text_id", "culture_additional_text", "id")

    assert error.source_table == "culture"
    assert error.source_column == "culture_additional_text_id"
    assert error.target_table == "culture_additional_text"
    assert error.target_column == "id"
    assert str(error) == (
        "Cannot resolve Foreing Key: culture.culture_additional_text_id -> culture_additional_text.id"
    )
