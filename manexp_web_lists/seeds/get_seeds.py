from pathlib import Path

import polars as pl

# Countries
from .extract.create_countries import create_countries

# Register subtypes
from .extract.create_register_subtypes import create_register_subtypes

# Register types
from .extract.create_register_types import create_register_types

# Plant varieties
from .extract.download_plant_varieties import download_plant_varieties

# Taxonomy
from .extract.download_taxonomy import download_taxonomy
from .load.load_seeds import load_seeds
from .transform.booleanize_plant_varieties import booleanize_plant_varieties
from .transform.clean_plant_varieties_denominations import clean_plant_varieties_denominations
from .transform.clean_taxonomy import clean_taxonomy
from .transform.color_taxonomy import color_taxonomy
from .transform.filter_plant_varieties import filter_plant_varieties
from .transform.filter_taxonomy import filter_taxonomy
from .transform.iconize_taxonomy import iconize_taxonomy
from .transform.merge_taxonomy import merge_taxonomy
from .transform.replace_plant_varieties_relations import replace_plant_varieties_relations
from .transform.translate_countries import translate_countries

FILES_PATH = Path("./seeds/files/")


def get_seeds() -> None:
    """
    Function to fetch, enrich, validate and load seeds lists
    """

    # Create files path if it doesn't exist
    FILES_PATH.mkdir(parents=True, exist_ok=True)

    # Extract and enrich countries list
    raw_countries_file = FILES_PATH / "raw_countries.csv"
    create_countries(raw_countries_file)
    output_countries = FILES_PATH / "country.parquet"
    translate_countries(pl.read_csv(raw_countries_file)).write_parquet(output_countries)

    # Create register types
    output_register_types = FILES_PATH / "register_type.parquet"
    create_register_types(output_register_types)

    # Created register subtypes
    output_register_subtypes = FILES_PATH / "register_subtype.parquet"
    create_register_subtypes(output_register_subtypes)

    # Extract, clean and enrich plant varieties
    raw_plant_varieties_file = FILES_PATH / "raw_plant_varieties.csv"
    download_plant_varieties(raw_plant_varieties_file)
    filtered_plant_varieties = filter_plant_varieties(pl.read_csv(raw_plant_varieties_file, infer_schema_length=0))
    booleanized_plant_varieties = booleanize_plant_varieties(filtered_plant_varieties)
    cleaned_plant_varieties = clean_plant_varieties_denominations(booleanized_plant_varieties)
    output_plant_varieties = FILES_PATH / "seed.parquet"
    replace_plant_varieties_relations(
        cleaned_plant_varieties,
        pl.read_parquet(output_countries),
        pl.read_parquet(output_register_types),
        pl.read_parquet(output_register_subtypes),
    ).write_parquet(output_plant_varieties)

    # Extract, clean and enrich taxonomy
    merged_file = FILES_PATH / "merged_taxonomy.csv"
    download_taxonomy(FILES_PATH)
    merge_taxonomy(FILES_PATH, merged_file)
    filtered_taxonomy = filter_taxonomy(pl.read_csv(merged_file), output_plant_varieties)
    cleaned_taxonomy = clean_taxonomy(filtered_taxonomy)
    iconized_taxonomy = iconize_taxonomy(cleaned_taxonomy)
    color_taxonomy(iconized_taxonomy).write_parquet(FILES_PATH / "taxon.parquet")

    # Load data
    load_seeds(FILES_PATH)

    # Clean lists folder
    for item in FILES_PATH.iterdir():
        item.unlink()
