from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Define a strict model for pydantic classes"""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,
        strict=True,
    )
