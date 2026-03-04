from typing import Optional

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.translations import Translation


class TranslationReport(StrictModel):
    """Represent the translation report model"""

    fr: Optional[Translation]
    en: Optional[Translation]
    de: Optional[Translation]
    it: Optional[Translation]


class CompleteTranslationReport(TranslationReport):
    """Represent the complete translation report model"""

    fr: Translation
    en: Translation
    de: Translation
    it: Translation


LANGUAGES = ["fr", "en", "de", "it"]
HUMAN_LANGUAGES = {"fr": "french", "en": "english", "de": "german", "it": "italian"}
GBIF_LANGUAGES = {"fr": "fra", "en": "eng", "de": "deu", "it": "ita"}
