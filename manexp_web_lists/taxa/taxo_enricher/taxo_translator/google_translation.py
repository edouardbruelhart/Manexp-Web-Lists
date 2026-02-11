from deep_translator import GoogleTranslator

from manexp_web_lists.taxa.models.taxa import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.models import TranslationReport


def translate_with_google(translation_report: TranslationReport) -> TranslationReport:
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

    def translate(dest: str) -> str:
        return GoogleTranslator(source=src, target=dest).translate(base)

    return TranslationReport(
        fr=translation_report.fr or Translation(name=translate("fr"), source=TranslationSource.GOOGLE),
        en=translation_report.en or Translation(name=translate("en"), source=TranslationSource.GOOGLE),
        de=translation_report.de or Translation(name=translate("de"), source=TranslationSource.GOOGLE),
        it=translation_report.it or Translation(name=translate("it"), source=TranslationSource.GOOGLE),
    )
