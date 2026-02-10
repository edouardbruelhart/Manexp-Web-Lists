from pathlib import Path
from typing import Optional

import requests

from manexp_web_lists.exceptions.fetch_exception import FetchException
from manexp_web_lists.utils.strict_model import StrictModel
from manexp_web_lists.varieties.models.taxons import RawTaxons, ResolvedTaxon, ResolvedTaxons, TaxonRank
from manexp_web_lists.varieties.utils.save_taxons import save_taxons


class ResolutionReport(StrictModel):
    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]


session = requests.Session()


def taxo_resolver(input_taxons: RawTaxons) -> ResolvedTaxons:
    """Resolve and clean taxonomy"""
    taxon_list: list[ResolvedTaxon] = []

    for taxon in input_taxons.taxons:
        # Replace wrong taxon for fragaria
        species = taxon.species if taxon.species != "Fragaria xananassa Duch." else "Fragaria ananassa"

        genus = taxon.genus if taxon.genus != "xTriticosecale Wittm. ex A. Camus" else "Triticosecale"

        submitted_taxon = species if species else genus

        if submitted_taxon is None:
            print(f"Skipping taxon {taxon} due to missing species and genus")
            continue

        resolution_report = resolve_taxo(submitted_taxon, taxon.taxon_rank)

        # Ignore entries where resolution fails
        if resolution_report is None:
            continue

        family = resolution_report.family if resolution_report.family is not None else taxon.family
        genus = resolution_report.genus if resolution_report.genus is not None else taxon.genus
        species = resolution_report.species

        # Ignore entries that are not resolved at family and genus level
        if family is None or genus is None:
            print(f"Skipped species {taxon.species} due to missing upper taxonomy: {taxon}")
            continue

        taxon_list.append(
            ResolvedTaxon(
                crop_category=taxon.crop_category,
                taxon_rank=taxon.taxon_rank,
                family=family,
                genus=genus,
                species=species,
                crops=taxon.crops,
            )
        )

    resolved_taxons = ResolvedTaxons(taxons=taxon_list)

    save_taxons(resolved_taxons, Path("../lists/in/resolved/resolved_taxon_list.json"))

    return resolved_taxons


def resolve_taxo(taxon: str, rank: TaxonRank) -> ResolutionReport | None:
    """Resolve and clean taxonomy using global names resolver."""

    url = "https://finder.globalnames.org/api/v1/find"

    payload = {
        "text": taxon,
        "format": "json",
        "bytesOffset": False,
        "returnContent": True,
        "uniqueNames": True,
        "ambiguousNames": True,
        "noBayes": False,
        "oddsDetails": False,
        "language": "eng",
        "wordsAround": 0,
        "verification": True,
        "sources": [1, 12, 169],
        "allMatches": True,
    }

    try:
        response = session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        best = data["names"][0]["verification"]["bestResult"]

        if not best:
            print(f"No match found for taxon '{taxon}' with rank {rank.name}")
            return None

        if not best.get("classificationPath") or not best.get("classificationRanks"):
            print(f"No classification found for taxon '{taxon}' with rank {rank.name}")
            return None

        path = best["classificationPath"].split("|")
        ranks = best["classificationRanks"].split("|")

        taxonomy = dict(zip(ranks, path))

        family = taxonomy.get("family")
        genus = taxonomy.get("genus")
        cleaned_species = taxonomy.get("species") if taxonomy.get("species") else best["matchedCanonicalFull"]

        if not cleaned_species:
            print(f"Skipping taxon '{taxon}' with rank {rank.name} due to missing species resolution: {best}")
            return None

        return ResolutionReport(
            family=family, genus=genus, species=cleaned_species if rank == TaxonRank.SPECIES else None
        )
    except requests.RequestException as e:
        raise FetchException(taxon, str(e)) from e
