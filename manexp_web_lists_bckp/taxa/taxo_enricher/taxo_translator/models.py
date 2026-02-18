from typing import Optional

from manexp_web_lists.taxa.taxon_models.taxa import Translation
from manexp_web_lists.utils.strict_model import StrictModel


class TranslationReport(StrictModel):
    """Represents the translation report model"""

    fr: Optional[Translation]
    en: Optional[Translation]
    de: Optional[Translation]
    it: Optional[Translation]


class CompleteTranslationReport(TranslationReport):
    fr: Translation
    en: Translation
    de: Translation
    it: Translation
