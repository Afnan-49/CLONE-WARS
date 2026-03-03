# app/models/review.py
from __future__ import annotations

from app.models.base_model import BaseModel
from app.models.validators import require_str, require_int


class Review(BaseModel):
    def __init__(self, text: str, rating: int, place_id: str, user_id: str) -> None:
        super().__init__()
        self.text = require_str("text", text)
        self.rating = require_int("rating", rating)

        if not isinstance(place_id, str) or place_id.strip() == "":
            raise ValueError("place_id is required")
        if not isinstance(user_id, str) or user_id.strip() == "":
            raise ValueError("user_id is required")

        self.place_id = place_id.strip()
        self.user_id = user_id.strip()

        self.validate()

    def validate(self) -> None:
        self.text = require_str("text", self.text)
        self.rating = require_int("rating", self.rating)
        if not (1 <= self.rating <= 5):
            raise ValueError("rating must be between 1 and 5")

        if not isinstance(self.place_id, str) or self.place_id.strip() == "":
            raise ValueError("place_id is required")
        if not isinstance(self.user_id, str) or self.user_id.strip() == "":
            raise ValueError("user_id is required")

    def update(self, data: dict) -> None:
        super().update(data)
        self.validate()
