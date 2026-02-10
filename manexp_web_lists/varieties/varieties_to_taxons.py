from pathlib import Path

from manexp_web_lists.varieties.models.crops import Crop, Crops
from manexp_web_lists.varieties.models.taxons import RawTaxon, RawTaxons, TaxonRank
from manexp_web_lists.varieties.models.varieties import Varieties
from manexp_web_lists.varieties.utils.save_taxons import save_taxons


def varieties_to_taxons(varieties: Varieties) -> RawTaxons:
    taxon_map: dict[tuple, RawTaxon] = {}

    for var in varieties.varieties:
        group_key = (var.botanical_info.family, var.botanical_info.genus, var.botanical_info.species)

        # Skip varieties without denomination
        if var.current_denomination is None:
            continue

        species = var.botanical_info.species if var.botanical_info.species != var.botanical_info.genus else None

        crop = Crop(
            id=var.id,
            status=var.status,
            upov_code=var.botanical_info.upov_code,
            denomination=var.current_denomination.denomination,
        )

        if group_key not in taxon_map:
            taxon_map[group_key] = RawTaxon(
                taxon_rank=TaxonRank.SPECIES if species else TaxonRank.GENUS,
                crop_category=var.crop_category,
                family=var.botanical_info.family,
                genus=var.botanical_info.genus,
                species=species,
                crops=Crops(crops=[crop]),
            )
        else:
            taxon_map[group_key].crops.crops.append(crop)

    taxons = RawTaxons(taxons=list(taxon_map.values()))

    save_taxons(taxons, Path("../lists/in/raw/raw_taxon_list.json"))

    return taxons
