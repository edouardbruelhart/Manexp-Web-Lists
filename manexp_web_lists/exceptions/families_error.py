from pathlib import Path


class FamiliesError(Exception):
    """
    Raised when actual families to icon mapping is not matching new dataset families
    """

    def __str__(self) -> str:
        # Local import to avoid circular dependency
        import manexp_web_lists.taxa.icon_generator.icon_generator as families_module

        path = Path(families_module.__file__).resolve()
        return (
            "New dataset families don't match old dataset families.\n"
            "Please update FAMILY_TO_ICON in:\n"
            f"{path}\n"
            "and re-run the script."
        )
