CORRECTION_DICTIONARY = {
    "Fragaria xananassa Duch.": "Fragaria ananassa",
    "xTriticosecale Wittm. ex A. Camus": "Triticosecale",
    "Triticum aestivum L. subsp. spelta (L.) Thell.": "Triticum aestivum subsp. spelta",
}


def apply_manual_correction(focal_name: str) -> str:
    """Apply manual corrections to focal names using CORRECTION_DICTIONARY."""
    return CORRECTION_DICTIONARY.get(focal_name, focal_name)
