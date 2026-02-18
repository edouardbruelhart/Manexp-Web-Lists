import inspect

import manexp_web_lists.taxa.icon_generator.models.families as families_module


class FamiliesException(Exception):
    def __str__(self) -> str:
        path = inspect.getfile(families_module)
        return (
            "New dataset families don't match old dataset families.\n"
            f"Please update FAMILIES dictionary in:\n{path}\n"
            "and re-run the script."
        )
