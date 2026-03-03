from __future__ import annotations

from app import db
from app.models.base_model import BaseModel
from app.models.associations import place_amenities

class Place(BaseModel):
    __tablename__ = "places"

    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), default="", nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
        )
    
    owner = db.relationship("User", back_populates="places")   
        
    reviews = db.relationship(
    "Review",
    back_populates="place",
    cascade="all, delete-orphan"
)
    amenities = db.relationship(
    "Amenity",
    secondary=place_amenities,
    back_populates="places",
    lazy="subquery",
)
           
    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title is required")
        if self.price is None:
            raise ValueError("Price is required")
        if self.latitude is None:
            raise ValueError("Latitude is required")
        if self.longitude is None:
            raise ValueError("Longitude is required")
        if not self.owner_id or not str(self.owner_id).strip():
            raise ValueError("Owner id is required")
