from enum import Enum


class Icons(str, Enum):
    """Defines the different icons for taxa"""

    CEREALS = "wheat"
    ORNAMENTAL = "deceased"
    MEDICINAL = "pill"
    HERBS = "grass"
    FRUITS = "nutrition"
    VEGETABLES = "restaurant"
    TREES = "nature"
    SUCCULENTS = "spa"
