from manexp_web_lists.utils.strict_model import StrictModel


class Translations(StrictModel):
    fr: str
    en: str
    de: str
    it: str


class Species(StrictModel):
    crop_category: str
    family: str
    genus: str
    species: str
    translations: Translations
    color: str
    icon: str


class SpeciesList(StrictModel):
    species: list[Species]
