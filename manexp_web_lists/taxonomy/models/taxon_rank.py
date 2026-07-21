from enum import Enum


class TaxonRank(str, Enum):
    """
    Represent the rank of the taxon
    """

    CULTIVAR = "cultivar group"
    VARIETY = "var."
    SUBSPECIES = "subsp."
    INFRASPECIES = "infrasp."
    MORPH = "morph"
    SPECIES = "sp."
    SUBGENUS = "subgen."
    GENUS = "gen."

    UNKNOWN = "unknown"
