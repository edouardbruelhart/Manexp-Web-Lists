from pathlib import Path
from typing import Optional

import requests

from manexp_web_lists.exceptions.fetch_exception import FetchException
from manexp_web_lists.taxa.models.crops import Crops
from manexp_web_lists.taxa.models.taxa import (
    RawTaxa,
    RawTaxonomy,
    ResolvedClassification,
    ResolvedTaxa,
    ResolvedTaxon,
    ResolvedTaxonomy,
    TaxonRank,
)
from manexp_web_lists.taxa.taxo_enricher.taxo_resolver.correction_dictionnary import apply_manual_correction
from manexp_web_lists.taxa.utils.save_taxa import save_taxa
from manexp_web_lists.utils.strict_model import StrictModel


# Structure to hold resolution result
class ResolutionReport(StrictModel):
    """Represents the resolution report model"""

    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]


# Default resquest session that can be customized globally
session = requests.Session()


def taxo_resolver(input_taxa: RawTaxa) -> ResolvedTaxa:
    """Resolve, clean and group taxonomy"""

    # Dictionary to hold resolved taxa
    grouped_taxa: dict[tuple, ResolvedTaxon] = {}

    # Resolve each taxon
    for taxon in input_taxa.taxa:
        # Get resolution
        resolution_report = resolve_taxo(taxon.taxonomy)

        # Ignore entries where resolution fails
        if resolution_report is None:
            continue

        # Infer resolved taxonomy
        family = (
            resolution_report.family or taxon.taxonomy.raw_classification.family.split(" ")[0]
            if taxon.taxonomy.raw_classification.family
            else None
        )
        genus = (
            resolution_report.genus or taxon.taxonomy.raw_classification.genus.split(" ")[0]
            if taxon.taxonomy.raw_classification.genus
            else None
        )
        species = resolution_report.species

        # Ignore entries that are not resolved at family and genus level
        if family is None or genus is None:
            print(f"Skipped {taxon.taxonomy.raw_classification.species} due to missing upper taxonomy: {taxon}")
            continue

        # Create key
        key = (family, genus, species)

        # If already exists, merge crops and categories
        if key in grouped_taxa:
            # Get existing entry
            existing = grouped_taxa[key]

            # Check that crop category is the same
            if existing.crop_category != taxon.crop_category:
                raise FetchException(taxon.taxonomy.raw_classification.focal_name, "Crop category mismatch")

            # Merge crops
            crops = Crops(crops=existing.crops.crops + taxon.crops.crops)

            new = ResolvedTaxon(
                crop_category=existing.crop_category,
                taxonomy=existing.taxonomy,
                crops=crops,
            )

            # Replace in the dict
            grouped_taxa[key] = new
        else:
            # Create classification and add new entry
            resolved_classification = ResolvedClassification(
                family=family, genus=genus, species=species, focal_name=species if species else genus
            )
            resolved_taxonomy = ResolvedTaxonomy(
                rank=taxon.taxonomy.rank,
                raw_classification=taxon.taxonomy.raw_classification,
                resolved_classification=resolved_classification,
            )
            grouped_taxa[key] = ResolvedTaxon(
                crop_category=taxon.crop_category,
                taxonomy=resolved_taxonomy,
                crops=taxon.crops,
            )

    # Create resolved taxa
    resolved_taxa = ResolvedTaxa(taxa=list(grouped_taxa.values()))

    # Save taxa to json file
    save_taxa(resolved_taxa, Path("../lists/in/resolved/resolved_taxon_list.json"))

    # Return resolved taxa
    return resolved_taxa


def resolve_taxo(taxonomy: RawTaxonomy) -> Optional[ResolutionReport]:
    """Resolve and clean taxonomy using global names resolver."""

    # API url
    url = "https://finder.globalnames.org/api/v1/find"

    # Isolate frequently used variables
    focal_name = apply_manual_correction(taxonomy.raw_classification.focal_name)
    rank = taxonomy.rank

    # Construct payload
    payload = {
        "text": focal_name,  # Input text
        "format": "json",  # Response format
        "bytesOffset": False,  # Only necessary when submitting text with multiple focal names
        "returnContent": True,  # Returns submitted content. Useful for debug, could be set to False in production
        "uniqueNames": True,  # Returns only unique names
        "ambiguousNames": True,  # Includes ambiguous names. Useful for taxonomy resolution
        "noBayes": False,  # Bayesian scoring for disambiguation
        "oddsDetails": False,  # Returns only useful Bayesian results
        "language": "eng",  #  Language of the input text. Useful only for long text detection, which is not our case.
        "wordsAround": 0,  # Number of words included around detected names. Useful only for long text detection, which is not our case.
        "verification": True,  # Verifies names on trusted sources. Essential to avoid garbage identification
        "sources": [1, 12, 169],  # Trusted sources selection. Here 1 = COL, 12 = GBIF Backbone and 169 = NCBI
        "allMatches": True,  # Returns all matches. Usefull for disambiguation
    }

    try:
        # Request
        response = session.post(url, json=payload)
        response.raise_for_status()

        # Get data
        data = response.json()

        # Get the best result
        best = data["names"][0]["verification"]["bestResult"]

        # If no best result stop resolution
        if not best:
            print(f"No match found for taxon {focal_name} with rank {rank.name}")
            return None

        # If no classification stop resolution
        if not best.get("classificationPath") or not best.get("classificationRanks"):
            print(f"No classification found for taxon '{focal_name}' with rank {rank.name}")
            return None

        # Format classification
        path = best["classificationPath"].split("|")
        ranks = best["classificationRanks"].split("|")
        classification = dict(zip(ranks, path))

        # Get useful information
        family = classification.get("family")
        genus = classification.get("genus")
        cleaned_species = classification.get("species") or best["matchedCanonicalFull"]

        # If no resolved species stop resolution
        if not cleaned_species:
            print(f"Skipping taxon '{focal_name}' with rank {rank.name} due to missing species resolution: {best}")
            return None

        # Return resolution report
        return ResolutionReport(
            family=family, genus=genus, species=cleaned_species if rank == TaxonRank.SPECIES else None
        )
    except requests.RequestException as e:
        raise FetchException(focal_name, str(e)) from e
