import logging
from pathlib import Path

from manexp_web_lists.exceptions.crop_category_mismatch import CropCategoryMismatchError
from manexp_web_lists.taxa.models.crops import Crops
from manexp_web_lists.taxa.models.taxa import CleanedTaxa, CleanedTaxon, RawTaxa
from manexp_web_lists.taxa.models.taxonomy import CleanedClassification, CleanedTaxonomy
from manexp_web_lists.taxa.save_taxa import save_taxa
from manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy import clean_taxonomy

# Initialize logger
logger = logging.getLogger(__name__)

CLEANED_PATH = Path("../lists/in/cleaned/cleaned_taxon_list.json")


def taxo_cleaner(input_taxa: RawTaxa) -> CleanedTaxa:
    """
    Clean and group taxonomy

    Args:
        input_taxa: Raw taxon list

    Returns:
        CleanedTaxa: Cleaned taxon list

    Raises:
        CropCategoryMismatchError: Raised when crop categories mismatch between two identical taxa
    """

    # Dictionary to hold cleaned taxa
    grouped_taxa: dict[tuple, CleanedTaxon] = {}

    # Clean each taxon
    for taxon in input_taxa.taxa:
        # Get cleaning
        cleaning_report = clean_taxonomy(taxon.taxonomy)

        # Ignore entries where cleaning fails
        if cleaning_report is None:
            continue

        # Create cleaned focal name
        focal_name = cleaning_report.species if cleaning_report.species else cleaning_report.genus

        # Create matching key
        key = (cleaning_report.family, cleaning_report.genus, cleaning_report.species)

        # If already exists, merge crops and categories
        if key in grouped_taxa:
            # Get existing entry
            existing = grouped_taxa[key]

            # Check that crop category is the same
            if existing.crop_category != taxon.crop_category:
                raise CropCategoryMismatchError(focal_name, existing.crop_category, taxon.crop_category)

            # Merge crops
            crops = Crops(crops=existing.crops.crops + taxon.crops.crops)

            new = CleanedTaxon(
                crop_category=existing.crop_category,
                taxonomy=existing.taxonomy,
                crops=crops,
            )

            # Replace in the dict
            grouped_taxa[key] = new
        else:
            # Create classification and add new entry
            cleaned_classification = CleanedClassification(
                family=cleaning_report.family,
                genus=cleaning_report.genus,
                species=cleaning_report.species,
                focal_name=focal_name,
            )
            cleaned_taxonomy = CleanedTaxonomy(
                rank=taxon.taxonomy.rank,
                raw_classification=taxon.taxonomy.raw_classification,
                cleaned_classification=cleaned_classification,
            )
            grouped_taxa[key] = CleanedTaxon(
                crop_category=taxon.crop_category,
                taxonomy=cleaned_taxonomy,
                crops=taxon.crops,
            )

    # Create cleaned taxa
    cleaned_taxa = CleanedTaxa(taxa=list(grouped_taxa.values()))

    # Save taxa to json file
    save_taxa(cleaned_taxa, CLEANED_PATH)

    logger.info(f"Done! Cleaned {len(cleaned_taxa.taxa)} taxa.")

    # Return cleaned taxa
    return cleaned_taxa
