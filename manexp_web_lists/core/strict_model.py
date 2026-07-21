from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict
from typing_extensions import override


class StrictModel(BaseModel):
    """
    Enforced BaseModel.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,
        strict=True,
    )

    @override
    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """
        An overriden model_dump to load key instead of name enum values.

        Args:
            **kwargs: Additional keyword arguments passed to the parent implementation.

        Returns:
            dict[str, Any]: The serialized model.
        """
        data = super().model_dump(**kwargs)

        for key, _value in data.items():
            obj = getattr(self, key)
            if isinstance(obj, Enum):
                data[key] = obj.name

        return data
