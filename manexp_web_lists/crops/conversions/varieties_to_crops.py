from manexp_web_lists.crops.models.crops import Crop, Crops
from manexp_web_lists.crops.models.varieties import Varieties


def varieties_to_crops(varieties: Varieties) -> Crops:
    crops: list[Crop] = []

    for variety in varieties.varieties:
        botanical = variety.botanical_info
        denomination = variety.current_denomination

        # Skip entries without a denomination if needed
        if denomination is None or botanical.species is None:
            continue

        crops.append(
            Crop(
                id=variety.id,
                status=variety.status,
                crop_category=variety.crop_category,
                family=botanical.family,
                genus=botanical.genus,
                species=botanical.species,
                upov_code=botanical.upov_code,
                denomination=denomination.denomination,
            )
        )

    return Crops(crops=crops)
