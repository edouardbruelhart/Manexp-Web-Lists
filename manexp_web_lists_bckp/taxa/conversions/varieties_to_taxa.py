import logging
from pathlib import Path

from manexp_web_lists.taxa.taxon_models.crops import Crop, Crops
from manexp_web_lists.taxa.taxon_models.taxa import RawClassification, RawTaxa, RawTaxon, RawTaxonomy, TaxonRank
from manexp_web_lists.taxa.taxon_models.varieties import Varieties
from manexp_web_lists.taxa.utils.save_taxa import save_taxa

# Initialize logger
logger = logging.getLogger(__name__)


def varieties_to_taxa(varieties: Varieties) -> RawTaxa:

    # Map to hold conversion
    taxon_map: dict[tuple, RawTaxon] = {}

    for var in varieties.varieties:
        # Remove genus values in species fields
        species = var.botanical_info.species if var.botanical_info.species != var.botanical_info.genus else None

        # Infer focal name
        focal_name = species if species else var.botanical_info.genus

        # Skip varieties without species AND genus
        if focal_name is None:
            logger.warning(f"Skipping {var.id}: No species or genus found.")
            continue

        # Skip varieties without denomination
        if var.current_denomination is None:
            logger.warning(f"Skipping {focal_name}: No denomination found.")
            continue

        # Create key to identify similar taxa
        group_key = (var.botanical_info.family, var.botanical_info.genus, var.botanical_info.species)

        # Create crop
        crop = Crop(
            id=var.id,
            status=var.status,
            upov_code=var.botanical_info.upov_code,
            denomination=var.current_denomination.denomination,
        )

        # Fill the map
        if group_key not in taxon_map:
            # Create classification
            raw_classification = RawClassification(
                family=var.botanical_info.family, genus=var.botanical_info.genus, species=species, focal_name=focal_name
            )

            # Create taxonomy
            raw_taxonomy = RawTaxonomy(
                rank=TaxonRank.SPECIES if species else TaxonRank.GENUS, raw_classification=raw_classification
            )

            # Create taxon
            taxon_map[group_key] = RawTaxon(
                crop_category=var.crop_category,
                taxonomy=raw_taxonomy,
                crops=Crops(crops=[crop]),
            )
        else:
            # Add crop to existing taxon
            taxon_map[group_key].crops.crops.append(crop)

    # Create raw taxa
    taxa = RawTaxa(taxa=list(taxon_map.values()))

    # Save raw taxa to JSON file
    save_taxa(taxa, Path("../lists/in/raw/raw_taxon_list.json"))

    # Return raw taxa
    return taxa
