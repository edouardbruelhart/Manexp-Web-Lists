from manexp_web_lists.requests.google_requests import translate
from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport


def google_translation(translation_report: TranslationReport) -> TranslationReport:
    """
    Get translations using Google API

    Args:
        translation_report: The translation report to update

    Returns:
        TranslationReport: The translation report for the specific taxon
    """

    base = (
        translation_report.en.name
        if translation_report.en
        else translation_report.fr.name
        if translation_report.fr
        else translation_report.de.name
        if translation_report.de
        else translation_report.it.name
        if translation_report.it
        else None
    )

    src = (
        "en"
        if translation_report.en
        else "fr"
        if translation_report.fr
        else "de"
        if translation_report.de
        else "it"
        if translation_report.it
        else None
    )

    # Nothing to translate
    if base is None or src is None:
        return translation_report

    return TranslationReport(
        fr=translation_report.fr or Translation(name=translate(base, src, "fr"), source=TranslationSource.GOOGLE),
        en=translation_report.en or Translation(name=translate(base, src, "en"), source=TranslationSource.GOOGLE),
        de=translation_report.de or Translation(name=translate(base, src, "de"), source=TranslationSource.GOOGLE),
        it=translation_report.it or Translation(name=translate(base, src, "it"), source=TranslationSource.GOOGLE),
    )
