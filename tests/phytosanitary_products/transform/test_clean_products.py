from pathlib import Path
from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.phytosanitary_products.transform.clean_products import (
    clean_products,
)


def test_clean_products(tmp_path: Path) -> None:
    products = pl.DataFrame({
        "id": ["product-1"],
        "name": ["Product 1"],
        "authorization_number": ["AUTH-123"],
        "soldout_deadline": ["2025-12-31 00:00:00.000"],
        "exhaustion_deadline": ["2026-12-31 00:00:00.000"],
        "product_category": [["category-1", "category-2"]],
        "formulation_code": [["formulation-1"]],
        "danger_symbol": [["danger-1", "danger-2"]],
        "signal_word": [["signal-1"]],
        "s_code": [["S1", "S2"]],
        "r_code": [["R1", "R2"]],
        "indication": [["indication-1", "indication-2"]],
    })

    with patch(
        "manexp_web_lists.phytosanitary_products.transform.clean_products.products_parser",
        return_value=products,
    ) as mock_parser:
        clean_products(tmp_path)

        result_products = pl.read_parquet(tmp_path / "products.parquet")

    mock_parser.assert_called_once()

    expected_products = pl.DataFrame({
        "id": ["product-1"],
        "name": ["Product 1"],
        "authorization_number": ["AUTH-123"],
        "soldout_deadline": pl.date_range(
            start=pl.date(2025, 12, 31),
            end=pl.date(2025, 12, 31),
            eager=True,
        ),
        "exhaustion_deadline": pl.date_range(
            start=pl.date(2026, 12, 31),
            end=pl.date(2026, 12, 31),
            eager=True,
        ),
    })

    assert_frame_equal(
        result_products,
        expected_products,
        check_row_order=False,
    )

    expected_product_category = pl.DataFrame({
        "product": [
            "product-1",
            "product-1",
        ],
        "product_category": [
            "category-1",
            "category-2",
        ],
    })

    result_product_category = pl.read_parquet(tmp_path / "product_product_category.parquet")

    assert_frame_equal(
        result_product_category,
        expected_product_category,
        check_row_order=False,
    )

    expected_formulation_code = pl.DataFrame({
        "product": ["product-1"],
        "formulation_code": ["formulation-1"],
    })

    result_formulation_code = pl.read_parquet(tmp_path / "product_formulation_code.parquet")

    assert_frame_equal(
        result_formulation_code,
        expected_formulation_code,
        check_row_order=False,
    )

    expected_danger_symbol = pl.DataFrame({
        "product": [
            "product-1",
            "product-1",
        ],
        "danger_symbol": [
            "danger-1",
            "danger-2",
        ],
    })

    result_danger_symbol = pl.read_parquet(tmp_path / "product_danger_symbol.parquet")

    assert_frame_equal(
        result_danger_symbol,
        expected_danger_symbol,
        check_row_order=False,
    )

    expected_signal_word = pl.DataFrame({
        "product": ["product-1"],
        "signal_word": ["signal-1"],
    })

    result_signal_word = pl.read_parquet(tmp_path / "product_signal_word.parquet")

    assert_frame_equal(
        result_signal_word,
        expected_signal_word,
        check_row_order=False,
    )

    expected_s_code = pl.DataFrame({
        "product": [
            "product-1",
            "product-1",
        ],
        "s_code": [
            "S1",
            "S2",
        ],
    })

    result_s_code = pl.read_parquet(tmp_path / "product_s_code.parquet")

    assert_frame_equal(
        result_s_code,
        expected_s_code,
        check_row_order=False,
    )

    expected_r_code = pl.DataFrame({
        "product": [
            "product-1",
            "product-1",
        ],
        "r_code": [
            "R1",
            "R2",
        ],
    })

    result_r_code = pl.read_parquet(tmp_path / "product_r_code.parquet")

    assert_frame_equal(
        result_r_code,
        expected_r_code,
        check_row_order=False,
    )

    expected_indication = pl.DataFrame({
        "product": [
            "product-1",
            "product-1",
        ],
        "indication": [
            "indication-1",
            "indication-2",
        ],
    })

    result_indication = pl.read_parquet(tmp_path / "product_indication.parquet")

    assert_frame_equal(
        result_indication,
        expected_indication,
        check_row_order=False,
    )
