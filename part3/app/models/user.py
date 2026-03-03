# app/models/user.py
from __future__ import annotations

from app import db, bcrypt
from app.models.base_model import BaseModel
from app.models.validators import require_str, require_email, require_bool


class User(BaseModel):
    __tablename__ = "users"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    reviews = db.relationship(
    "Review",
    back_populates="user",
    cascade="all, delete-orphan"
)
    places = db.relationship(
    "Place",
    back_populates="owner",
    cascade="all, delete-orphan",
)


    # -------------------------
    # Password Hashing
    # -------------------------
    def hash_password(self, password: str) -> None:
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    def validate(self) -> None:
        self.first_name = require_str("first_name", self.first_name, max_len=50)
        self.last_name = require_str("last_name", self.last_name, max_len=50)
        self.email = require_email(self.email)
        self.password = require_str("password", self.password, max_len=128)
        self.is_admin = require_bool("is_admin", self.is_admin)


    
