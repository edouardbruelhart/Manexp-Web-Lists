from deep_translator import GoogleTranslator


def translate(text: str, src_lang: str, dest_lang: str) -> str:
    """
    Translate the text

    Args:
        text: The text to translate
        src_lang: The source language
        dest_lang: The destination language

    Returns:
        str: The translated text
    """

    return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
