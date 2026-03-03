# app/models/amenity.py
from __future__ import annotations

from app.models.base_model import BaseModel
from app.models.validators import require_str


class Amenity(BaseModel):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = require_str("name", name, max_len=50)

    def validate(self) -> None:
        self.name = require_str("name", self.name, max_len=50)

    def update(self, data: dict) -> None:
        super().update(data)
        self.validate()
