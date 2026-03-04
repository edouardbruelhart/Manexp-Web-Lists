from manexp_web_lists.taxa.models.taxa import TranslatedTaxa


def get_unique_families(taxa: TranslatedTaxa) -> list[str]:
    """
    Get the actual list of families from taxon list

    Args:
        taxa: The translated taxon list

    Returns:
        list[str]: The actual list of families
    """

    unique_families: list[str] = []

    for taxon in taxa.taxa:
        family = taxon.taxonomy.cleaned_classification.family
        if family not in unique_families:
            unique_families.append(family)

    return unique_families
