# app/models/place.py
from __future__ import annotations

from typing import List, Optional

from app.models.base_model import BaseModel
from app.models.validators import require_str, optional_str, require_float


class Place(BaseModel):
    def __init__(
        self,
        title: str,
        description: Optional[str],
        price: float,
        latitude: float,
        longitude: float,
        owner_id: str,
    ) -> None:
        super().__init__()
        self.title = require_str("title", title, max_len=100)
        self.description = optional_str("description", description)
        self.price = require_float("price", price)
        self.latitude = require_float("latitude", latitude)
        self.longitude = require_float("longitude", longitude)

        if not isinstance(owner_id, str) or owner_id.strip() == "":
            raise ValueError("owner_id is required")
        self.owner_id = owner_id.strip()

        # Relationships (store IDs for simplicity)
        self.review_ids: List[str] = []
        self.amenity_ids: List[str] = []

        self.validate()

    def validate(self) -> None:
        self.title = require_str("title", self.title, max_len=100)
        self.description = optional_str("description", self.description)
        self.price = require_float("price", self.price)
        if self.price <= 0:
            raise ValueError("price must be a positive value")

        self.latitude = require_float("latitude", self.latitude)
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError("latitude must be between -90.0 and 90.0")

        self.longitude = require_float("longitude", self.longitude)
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("longitude must be between -180.0 and 180.0")

        if not isinstance(self.owner_id, str) or self.owner_id.strip() == "":
            raise ValueError("owner_id is required")

    def add_review_id(self, review_id: str) -> None:
        if not isinstance(review_id, str) or review_id.strip() == "":
            raise ValueError("review_id is required")
        rid = review_id.strip()
        if rid not in self.review_ids:
            self.review_ids.append(rid)
            self.save()

    def add_amenity_id(self, amenity_id: str) -> None:
        if not isinstance(amenity_id, str) or amenity_id.strip() == "":
            raise ValueError("amenity_id is required")
        aid = amenity_id.strip()
        if aid not in self.amenity_ids:
            self.amenity_ids.append(aid)
            self.save()

    def remove_amenity_id(self, amenity_id: str) -> None:
        aid = (amenity_id or "").strip()
        if aid in self.amenity_ids:
            self.amenity_ids.remove(aid)
            self.save()

    def update(self, data: dict) -> None:
        super().update(data)
        self.validate()
