from typing import Optional


class CropCategoryMismatchError(Exception):
    """
    Raised when crop categories mismatch between two identical taxa.

    Args:
        focal_name: Focal name of the taxon.
        first_crop_category: First crop category.
        second_crop_category: Second crop category.
    """

    def __init__(
        self,
        focal_name: Optional[str],
        first_crop_category: str,
        second_crop_category: str,
    ):
        super().__init__(self._format_message(focal_name, first_crop_category, second_crop_category))

    @staticmethod
    def _format_message(
        focal_name: Optional[str],
        first_crop_category: str,
        second_crop_category: str,
    ) -> str:
        message = f"Crop category mismatch for {focal_name}: {first_crop_category} != {second_crop_category}"
        return message
