"""Tests for taxa/save_taxa.py"""

from pathlib import Path

from pydantic import BaseModel

from manexp_web_lists.taxa.save_taxa import save_taxa


class DummyTaxa(BaseModel):
    name: str
    count: int


def test_save_taxa_writes_expected_json(tmp_path: Path):
    taxa = DummyTaxa(name="Apple", count=3)
    output_file = tmp_path / "taxa.json"

    save_taxa(taxa, output_file)

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert content == ('{\n  "name": "Apple",\n  "count": 3\n}')
