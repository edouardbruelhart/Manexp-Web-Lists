CORRECTION_DICTIONARY = {
    "Fragaria xananassa Duch.": "Fragaria ananassa",
    "Sempervivum xrupicola A. Kern.": "Sempervivum rupicola",
    "Impatiens New Guinea Group": "Impatiens novae-guinea",
    "Impatiens hawkeri W. Bull": "Impatiens novae-guinea",
    "Begonia Semperflorens-Cultorum Group": "Begonia semperflorens-cultorum",
    "Pericallis cruenta (Masson ex L'Hér.) Bolle": "Cineraria cruenta",
    "Bidens ferulifolia (Jacq.) DC.": "Bidens aurea",
}


def apply_manual_correction(focal_name: str) -> str:
    """
    Apply manual corrections to focal names using CORRECTION_DICTIONARY.

    Args:
        focal_name: Focal name to be corrected.

    Returns:
        str: Corrected focal name.
    """

    return CORRECTION_DICTIONARY.get(focal_name, focal_name)
