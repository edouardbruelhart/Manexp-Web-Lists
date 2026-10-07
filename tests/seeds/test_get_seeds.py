from unittest.mock import MagicMock, patch

from manexp_web_lists.seeds.get_seeds import get_seeds


def test_get_seeds(tmp_path) -> None:
    # Files that should be removed during cleanup.
    (tmp_path / "old_file.csv").touch()
    (tmp_path / "old_file.parquet").touch()

    with (
        patch("manexp_web_lists.seeds.get_seeds.FILES_PATH", tmp_path),
        patch("manexp_web_lists.seeds.get_seeds.create_countries") as create_countries,
        patch("manexp_web_lists.seeds.get_seeds.translate_countries") as translate_countries,
        patch("manexp_web_lists.seeds.get_seeds.create_register_types") as create_register_types,
        patch("manexp_web_lists.seeds.get_seeds.create_register_subtypes") as create_register_subtypes,
        patch("manexp_web_lists.seeds.get_seeds.download_plant_varieties") as download_plant_varieties,
        patch("manexp_web_lists.seeds.get_seeds.filter_plant_varieties") as filter_plant_varieties,
        patch("manexp_web_lists.seeds.get_seeds.booleanize_plant_varieties") as booleanize_plant_varieties,
        patch(
            "manexp_web_lists.seeds.get_seeds.clean_plant_varieties_denominations"
        ) as clean_plant_varieties_denominations,
        patch(
            "manexp_web_lists.seeds.get_seeds.replace_plant_varieties_relations"
        ) as replace_plant_varieties_relations,
        patch("manexp_web_lists.seeds.get_seeds.download_taxonomy") as download_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.merge_taxonomy") as merge_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.filter_taxonomy") as filter_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.clean_taxonomy") as clean_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.iconize_taxonomy") as iconize_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.color_taxonomy") as color_taxonomy,
        patch("manexp_web_lists.seeds.get_seeds.load_seeds") as load_seeds,
        patch("manexp_web_lists.seeds.get_seeds.pl.read_csv") as read_csv,
        patch("manexp_web_lists.seeds.get_seeds.pl.read_parquet") as read_parquet,
    ):
        # Input data
        countries = MagicMock(name="countries")
        raw_plant_varieties = MagicMock(name="raw_plant_varieties")
        merged_taxonomy = MagicMock(name="merged_taxonomy")

        # Reference parquet data
        country_data = MagicMock(name="country_data")
        register_types = MagicMock(name="register_types")
        register_subtypes = MagicMock(name="register_subtypes")

        # Transformation results
        translated_countries = MagicMock(name="translated_countries")
        filtered_plant_varieties = MagicMock(name="filtered_plant_varieties")
        booleanized_plant_varieties = MagicMock(name="booleanized_plant_varieties")
        cleaned_plant_varieties = MagicMock(name="cleaned_plant_varieties")
        replaced_plant_varieties = MagicMock(name="replaced_plant_varieties")

        filtered_taxonomy = MagicMock(name="filtered_taxonomy")
        cleaned_taxonomy = MagicMock(name="cleaned_taxonomy")
        iconized_taxonomy = MagicMock(name="iconized_taxonomy")
        colored_taxonomy = MagicMock(name="colored_taxonomy")

        read_csv.side_effect = [
            countries,
            raw_plant_varieties,
            merged_taxonomy,
        ]

        read_parquet.side_effect = [
            country_data,
            register_types,
            register_subtypes,
        ]

        translate_countries.return_value = translated_countries
        filter_plant_varieties.return_value = filtered_plant_varieties
        booleanize_plant_varieties.return_value = booleanized_plant_varieties
        clean_plant_varieties_denominations.return_value = cleaned_plant_varieties
        replace_plant_varieties_relations.return_value = replaced_plant_varieties

        filter_taxonomy.return_value = filtered_taxonomy
        clean_taxonomy.return_value = cleaned_taxonomy
        iconize_taxonomy.return_value = iconized_taxonomy
        color_taxonomy.return_value = colored_taxonomy

        get_seeds()

    # Countries
    raw_countries_file = tmp_path / "raw_countries.csv"
    output_countries = tmp_path / "country.parquet"

    create_countries.assert_called_once_with(raw_countries_file)
    translate_countries.assert_called_once_with(countries)
    translated_countries.write_parquet.assert_called_once_with(
        output_countries,
    )

    # Register tables
    create_register_types.assert_called_once_with(
        tmp_path / "register_type.parquet",
    )

    create_register_subtypes.assert_called_once_with(
        tmp_path / "register_subtype.parquet",
    )

    # Plant varieties
    raw_plant_varieties_file = tmp_path / "raw_plant_varieties.csv"

    download_plant_varieties.assert_called_once_with(
        raw_plant_varieties_file,
    )

    filter_plant_varieties.assert_called_once_with(
        raw_plant_varieties,
    )

    booleanize_plant_varieties.assert_called_once_with(
        filtered_plant_varieties,
    )

    clean_plant_varieties_denominations.assert_called_once_with(
        booleanized_plant_varieties,
    )

    replace_plant_varieties_relations.assert_called_once_with(
        cleaned_plant_varieties,
        country_data,
        register_types,
        register_subtypes,
    )

    replaced_plant_varieties.write_parquet.assert_called_once_with(
        tmp_path / "seed.parquet",
    )

    # Taxonomy
    merged_file = tmp_path / "merged_taxonomy.csv"

    download_taxonomy.assert_called_once_with(tmp_path)

    merge_taxonomy.assert_called_once_with(
        tmp_path,
        merged_file,
    )

    filter_taxonomy.assert_called_once_with(
        merged_taxonomy,
        tmp_path / "seed.parquet",
    )

    clean_taxonomy.assert_called_once_with(
        filtered_taxonomy,
    )

    iconize_taxonomy.assert_called_once_with(
        cleaned_taxonomy,
    )

    color_taxonomy.assert_called_once_with(
        iconized_taxonomy,
    )

    colored_taxonomy.write_parquet.assert_called_once_with(
        tmp_path / "taxon.parquet",
    )

    # Load
    load_seeds.assert_called_once_with(tmp_path)

    # Cleanup
    assert list(tmp_path.iterdir()) == []
