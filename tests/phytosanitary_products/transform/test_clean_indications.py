from pathlib import Path
from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.phytosanitary_products.transform.clean_indications import clean_indications


def test_clean_indications(tmp_path: Path) -> None:
    indications = pl.DataFrame({
        "dosage_from": ["1"],
        "dosage_to": ["2"],
        "waiting_period": ["3"],
        "expenditure_from": ["13.000000"],
        "expenditure_to": ["4"],
        "id": ["indication-1"],
        "measure": [["measure-1"]],
        "time_measure": [["time-measure-1"]],
        "application_area": [["application-area-1"]],
        "application_comment": [["comment-1", "comment-2"]],
        "culture": [[{"id": "culture-1", "additional_text": ""}, {"id": "culture-2", "additional_text": ""}]],
        "culture_form": [["outdoor", "indoor"]],
        "pest": [
            [
                {"id": "pest-1", "additional_text": "", "type": "PEST_FULL_EFFECT"},
                {"id": "pest-2", "additional_text": "", "type": "PEST_FULL_EFFECT"},
            ]
        ],
        "obligation": [["obligation-1", "obligation-2"]],
    })

    with patch(
        "manexp_web_lists.phytosanitary_products.transform.clean_indications.indications_parser",
        return_value=indications,
    ) as mock_parser:
        clean_indications(tmp_path)

        result_indications = pl.read_parquet(tmp_path / "indications.parquet")

    mock_parser.assert_called_once()

    expected_indications = pl.DataFrame({
        "dosage_from": ["1"],
        "dosage_to": ["2"],
        "waiting_period": ["3"],
        "expenditure_from": ["13.000000"],
        "expenditure_to": ["4"],
        "id": ["indication-1"],
    })

    assert_frame_equal(
        result_indications,
        expected_indications,
        check_row_order=False,
    )

    expected_measure = pl.DataFrame({
        "indication": ["indication-1"],
        "measure": ["measure-1"],
    })

    result_measure = pl.read_parquet(tmp_path / "indication_measure.parquet")

    assert_frame_equal(result_measure, expected_measure, check_row_order=False)

    expected_time_measure = pl.DataFrame({
        "indication": ["indication-1"],
        "time_measure": ["time-measure-1"],
    })

    result_time_measure = pl.read_parquet(tmp_path / "indication_time_measure.parquet")

    assert_frame_equal(
        result_time_measure,
        expected_time_measure,
        check_row_order=False,
    )

    expected_area = pl.DataFrame({
        "indication": [
            "indication-1",
        ],
        "application_area": [
            "application-area-1",
        ],
    })

    result_area = pl.read_parquet(tmp_path / "indication_application_area.parquet")

    assert_frame_equal(
        result_area,
        expected_area,
        check_row_order=False,
    )

    expected_comments = pl.DataFrame({
        "indication": [
            "indication-1",
            "indication-1",
        ],
        "application_comment": [
            "comment-1",
            "comment-2",
        ],
    })

    result_comments = pl.read_parquet(tmp_path / "indication_application_comment.parquet")

    assert_frame_equal(
        result_comments,
        expected_comments,
        check_row_order=False,
    )

    expected_culture = pl.DataFrame({
        "indication": [
            "indication-1",
            "indication-1",
        ],
        "culture": [
            "culture-1",
            "culture-2",
        ],
        "additional_text": [
            "",
            "",
        ],
    })

    result_culture = pl.read_parquet(tmp_path / "indication_culture.parquet")

    assert_frame_equal(
        result_culture,
        expected_culture,
        check_row_order=False,
    )

    expected_culture_form = pl.DataFrame({
        "indication": [
            "indication-1",
            "indication-1",
        ],
        "culture_form": [
            "outdoor",
            "indoor",
        ],
    })

    result_culture_form = pl.read_parquet(tmp_path / "indication_culture_form.parquet")

    assert_frame_equal(
        result_culture_form,
        expected_culture_form,
        check_row_order=False,
    )

    expected_pest = pl.DataFrame({
        "indication": [
            "indication-1",
            "indication-1",
        ],
        "pest": [
            "pest-1",
            "pest-2",
        ],
        "additional_text": [
            "",
            "",
        ],
        "type": [
            "PEST_FULL_EFFECT",
            "PEST_FULL_EFFECT",
        ],
    })

    result_pest = pl.read_parquet(tmp_path / "indication_pest.parquet")

    assert_frame_equal(
        result_pest,
        expected_pest,
        check_row_order=False,
    )

    expected_obligation = pl.DataFrame({
        "indication": [
            "indication-1",
            "indication-1",
        ],
        "obligation": [
            "obligation-1",
            "obligation-2",
        ],
    })

    result_obligation = pl.read_parquet(tmp_path / "indication_obligation.parquet")

    assert_frame_equal(
        result_obligation,
        expected_obligation,
        check_row_order=False,
    )
