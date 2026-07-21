import polars as pl
from polars import DataFrame

ICONS = {
    "Quercus": "🌳",
    "Pinus": "🌲",
    "Prunus": "🍒",
    "Brassica": "🥦",
    "Rosa": "🌹",
    "Triticum": "🌾",
    "Hordeum": "🌾",
    "Sorghum": "🌾",
    "Oryza": "🌾",
    "Avena": "🌾",
    "Triticosecale": "🌾",
    "Secale": "🌾",
    "Zea": "🌽",
    "Solanum": "🍅",
    "Citrus": "🍋",
    "Malus": "🍎",
    "Pyrus": "🍐",
    "Cydonia": "🍐",
    "Vitis": "🍇",
    "Cucumis": "🥒",
    "Sicyos": "🥒",
    "Pisum": "🫘",
    "Cucurbita": "🎃",
    "Lagenaria": "🎃",
    "Fragaria": "🍓",
    "Trifolium": "☘️",
    "Phleum": "🌿",
    "Raphanus": "🫜",
    "Vaccinium": "🫐",
    "Rubus": "🫐",
    "Ribes": "🫐",
    "Agrostis": "🌿",
    "Allium": "🧄",
    "Lupinus": "🌿",
    "Gossypium": "👖",
    "Glycine": "🫘",
    "Galega": "🌿",
    "Medicago": "☘️",
    "Phalaris": "🌿",
    "Ornithopus": "🌿",
    "Phaseolus": "🫘",
    "Poa": "🌿",
    "Corylus": "🌰",
    "Junglans": "🌰",
    "Beta": "🫜",
    "Anthriscus": "🌿",
    "Spinacia": "🥬",
    "Festuca": "🌿",
    "Vicia": "🌿",
    "Trigonella": "🌿",
    "Lolium": "🌿",
    "Ficus": "🌳",
    "Arrhenatherum": "🌿",
    "Festulolium": "🌿",
    "Bromus": "🌿",
    "Capsicum": "🌶️",
    "Daucus": "🥕",
    "Cynodon": "🌿",
    "Carum": "🌿",
    "Pistacia": "🫘",
    "Castanea": "🌰",
    "Sinapis": "🥦",
    "Cichorium": "🌿",
    "Lotus": "🌿",
    "Phacelia": "🌸",
    "Petroselinum": "🌿",
    "Foeniculum": "🥬",
    "Papaver": "🌸",
    "Carthamus": "🖌",
    "Arachis": "🥜",
    "Scorzonera": "🥕",
    "Olea": "🫒",
    "Lathyrus": "🫛",
    "Dactylis": "🌿",
    "Alopecurus": "🌿",
    "Lactuca": "🥗",
    "Onobrychis": "🌿",
    "Trisetum": "🌿",
    "Linum": "👖",
    "Plantago": "🌿",
    "Cannabis": "🍁",
    "Helianthus": "🌻",
    "Citrullus": "🍉",
    "Valerianella": "🥬",
    "Hedysarum": "🌿",
}


def iconize_taxonomy(taxonomy: DataFrame) -> DataFrame:
    """
    Add icons to the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe

    Returns:
        DataFrame: The iconized taxonomy list
    """

    iconized_taxonomy = taxonomy.with_columns(icon=(pl.col("genus").replace_strict(ICONS, default="🌱")))

    return iconized_taxonomy
