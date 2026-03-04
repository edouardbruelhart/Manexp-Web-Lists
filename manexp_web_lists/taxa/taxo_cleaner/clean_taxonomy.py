import logging
from typing import Optional

from pydantic import Field

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.requests.gbif_requests import gbif_parser_request
from manexp_web_lists.taxa.models.taxonomy import RawTaxonomy, TaxonRank
from manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy import resolve_taxonomy

# Initialize logger
logger = logging.getLogger(__name__)


# Structure to hold Cleaning result
class CleaningReport(StrictModel):
    """Represent the cleaning report model"""

    family: str = Field(..., description="Family of the taxon")
    genus: str = Field(..., description="Genus of the taxon")
    species: Optional[str] = Field(..., description="Species of the taxon")


def clean_taxonomy(taxonomy: RawTaxonomy) -> CleaningReport | None:
    """
    Clean taxonomy using GBIF name parser.

    Args:
        taxonomy: Raw taxonomy

    Returns:
        CleaningReport | None: Cleaning report
    """

    # Isolate frequently used variables
    rank = taxonomy.rank
    focal_name = taxonomy.raw_classification.focal_name
    species = taxonomy.raw_classification.species
    genus = taxonomy.raw_classification.genus
    family = taxonomy.raw_classification.family

    if species is None and genus is None:
        logger.warning(f"Skipping {focal_name} with rank {rank.name}: Missing species and genus.")
        return None

    # Get cleaned species
    cleaned_species = clean_name(species) if rank == TaxonRank.SPECIES else None

    # Try to parse dirty species by taking two first parts. Works in some cases
    if cleaned_species is None and species is not None:
        cropped = " ".join(species.split(" ")[:2])
        logger.info(f"Retrying with cropped species: {cropped}...")
        cleaned_species = clean_name(cropped)
        if cleaned_species is not None:
            logger.info("Cropped species successfully parsed!")
        else:
            logger.warning("Parsing also failed with cropped species.")

    # Get cleaned genus
    cleaned_genus = (
        clean_name(genus)
        if genus is not None
        else resolve_taxonomy(cleaned_species, TaxonRank.SPECIES, TaxonRank.GENUS)
        if cleaned_species is not None
        else None
    )

    # Try to parse dirty genus by taking first part. Works in some cases
    if cleaned_genus is None and genus is not None:
        cropped = genus.split(" ")[0]
        logger.info(f"Retrying with cropped genus: {cropped}...")
        cleaned_genus = clean_name(cropped)
        if cleaned_genus is not None:
            logger.info("Cropped genus successfully parsed!")
        else:
            logger.warning("Parsing also failed with cropped genus.")

    # Get cleaned family
    cleaned_family = (
        clean_name(family)
        if family is not None
        else resolve_taxonomy(cleaned_species, TaxonRank.SPECIES, TaxonRank.FAMILY)
        if cleaned_species is not None
        else resolve_taxonomy(cleaned_genus, TaxonRank.GENUS, TaxonRank.FAMILY)
        if cleaned_genus is not None
        else None
    )

    # Ignore crops thant have a raw given species that couldn't be cleaned
    if cleaned_species is None and rank == TaxonRank.SPECIES:
        logger.warning(f"Skipping {focal_name} with rank {rank.name}: Missing species resolution: {taxonomy}")

    # Ignore crops without cleaned upper taxonomy
    if cleaned_genus is None or cleaned_family is None:
        logger.warning(f"Skipping {focal_name} with rank {rank.name}: Upper taxonomy is lacking: {taxonomy}")
        return None

    # Return resolution report
    return CleaningReport(family=cleaned_family, genus=cleaned_genus, species=cleaned_species)


def clean_name(name: str | None) -> str | None:
    """
    Clean name using GBIF name parser.

    Args:
        name: Name to clean

    Returns:
        str | None: Cleaned name
    """

    if name is None:
        return None

    response = gbif_parser_request(name)

    if response is None:
        return None

    cleaned_name = response.get("canonicalName") if response.get("canonicalName") else None

    return cleaned_name
