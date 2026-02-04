from pathlib import Path

from manexp_web_lists.crops.conversions.varieties_to_crops import varieties_to_crops
from manexp_web_lists.crops.models.crops import Crops
from manexp_web_lists.crops.models.varieties import Varieties
from manexp_web_lists.json_client.client import JsonClient


def fetch_crops() -> None:
    """Main function to fetch and validate crops list."""

    # Variables
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    raw_file_path = Path("../lists/raw/varieties_list.json")
    crops_output_path = Path("../lists/treated/crops_list.json")

    # Client
    client = JsonClient()

    try:
        # 1. Use the client to download raw json
        client.download_file(url, raw_file_path)

        # 2. Load and validate the downloaded json
        varieties = client.load_file(raw_file_path, Varieties)

        # 3. Convert to crops model
        crops = varieties_to_crops(varieties)

        # 4. Save the validated crops list
        if not crops_output_path.exists():
            # If the file doesn't exist, write the new crops list directly
            save_crops(crops, crops_output_path)
        else:
            # If the file exists:

            # Load the existing crops list
            old_crops = client.load_file(crops_output_path, Crops)

            # Compare and merge if there are changes
            if old_crops != crops:
                # Index crops by id
                new_by_denomination = {crop.denomination: crop for crop in crops.crops}

                # Add new crops first
                merged = dict(new_by_denomination)

                # Then add old crops that are not in new crops
                for old_crop in old_crops.crops:
                    if old_crop.denomination not in merged:
                        merged[old_crop.denomination] = old_crop

                # Save the merged crops list
                merged_crops = Crops(crops=sorted(merged.values(), key=lambda c: c.denomination))

                # Write to file
                save_crops(merged_crops, crops_output_path)

    except Exception as e:
        # TODO: Uncomment the email notification once code is in production and remove print
        print(f"An error occurred in the main process: {e}")
        # mailer = Mailer()

        # mailer.send_email(subject="Error fetching crops list", body=f"An error occurred in the main process: {e}")


def save_crops(crops: Crops, path: Path) -> None:
    path.write_text(
        crops.model_dump_json(
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
