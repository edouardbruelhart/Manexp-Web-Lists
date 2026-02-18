from pathlib import Path

from manexp_web_lists.core.json_client import JsonClient


def fetch_taxa() -> None:
    """Function to fetch, enrich and validate taxon list."""

    # Variables
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    raw_file_path = Path("../lists/in/raw/varieties_list.json")
    # output_file_path = Path("../lists/out/generated_taxon_list.json")

    # Client
    client = JsonClient()

    # 1. Use the client to download raw json
    client.download_file(url, raw_file_path)

    # # 2. Load and validate the downloaded json
    # varieties = client.load_file(raw_file_path, Varieties)

    # # 3. Group varieties into taxons
    # log_sub_section("Converting varieties to taxa")
    # raw_taxa = varieties_to_taxa(varieties)

    # # 4. Resolve taxons
    # log_sub_section("Resolving taxa")
    # resolved_taxa = taxo_resolver(raw_taxa)

    # # 5. Add translations
    # log_sub_section("Translating taxa")
    # translated_taxa = taxo_translator(resolved_taxa)

    # # 6. Add icon for each taxon
    # # TODO: Start here for cleaning
    # iconed_taxa = icon_generator(translated_taxa)

    # # 7. Add color for each taxon
    # colored_taxa = color_generator(iconed_taxa)

    # # 8. Save the list
    # save_taxa(colored_taxa, output_file_path)
