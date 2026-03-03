from __future__ import annotations

from app import db
from app.models.base_model import BaseModel
from app.models.associations import place_amenities


class Amenity(BaseModel):
    __tablename__ = "amenities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, unique=True, index=True)
    
    places = db.relationship(
    "Place",
    secondary=place_amenities,
    back_populates="amenities",
    lazy="subquery",
)
    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Name is required")
