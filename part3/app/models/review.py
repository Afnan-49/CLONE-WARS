from __future__ import annotations

from app import db
from app.models.base_model import BaseModel


class Review(BaseModel):
    __tablename__ = "reviews"


    text = db.Column(db.String(1024), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")
    
    def validate(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("Text is required")
        if self.rating is None:
            raise ValueError("Rating is required")
        if not (1 <= int(self.rating) <= 5):
            raise ValueError("Rating must be between 1 and 5")
        if not self.user_id or not str(self.user_id).strip():
            raise ValueError("User id is required")
        if self.place_id is None:
            raise ValueError("Place id is required")
