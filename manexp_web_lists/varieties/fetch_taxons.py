from pathlib import Path

from manexp_web_lists.json_client.client import JsonClient
from manexp_web_lists.varieties.models.varieties import Varieties
from manexp_web_lists.varieties.taxo_enricher.taxo_resolver import taxo_resolver
from manexp_web_lists.varieties.taxo_enricher.taxo_translator import taxo_translator
from manexp_web_lists.varieties.varieties_to_taxons import varieties_to_taxons


def fetch_taxons() -> None:
    """Function to fetch, enrich and validate taxon list."""

    # Variables
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    raw_file_path = Path("../lists/in/raw/varieties_list.json")
    # taxons_output_path = Path("../lists/out/final_taxon_list.json")

    # Client
    client = JsonClient()

    # 1. Use the client to download raw json
    client.download_file(url, raw_file_path)

    # 2. Load and validate the downloaded json
    varieties = client.load_file(raw_file_path, Varieties)

    # 3. Group varieties into taxons
    raw_taxons = varieties_to_taxons(varieties)

    # 4. Resolve taxons
    resolved_taxons = taxo_resolver(raw_taxons)

    # 5. Add translations
    translated_species = taxo_translator(resolved_taxons)

    print(translated_species)

    # # 4. Save the enriched species list
    # if not taxons_output_path.exists():
    #     # If the file doesn't exist, write the new crops list directly
    #     save_species(species, taxons_output_path)
    # else:
    #     # If the file exists:

    #     # Load the existing crops list
    #     old_species = client.load_file(species_output_path, SpeciesList)

    #     # Compare and merge if there are changes
    #     if old_species != species:
    #         print("still to implement")
    #         # TODO: Implement this
    #         # # Index crops by id
    #         # new_by_denomination = {crop.denomination: crop for crop in crops.crops}

    #         # # Add new crops first
    #         # merged = dict(new_by_denomination)

    #         # # Then add old crops that are not in new crops
    #         # for old_crop in old_crops.crops:
    #         #     if old_crop.denomination not in merged:
    #         #         merged[old_crop.denomination] = old_crop

    #         # # Save the merged crops list
    #         # merged_crops = Crops(crops=sorted(merged.values(), key=lambda c: c.denomination))

    #         # # Write to file
    #         # save_crops(merged_crops, crops_output_path)
