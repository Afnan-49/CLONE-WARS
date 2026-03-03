# app/models/user.py
from __future__ import annotations

from app.models.base_model import BaseModel
from app.models.validators import require_str, require_email, require_bool


class User(BaseModel):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        is_admin: bool = False,
    ) -> None:
        super().__init__()
        self.first_name = require_str("first_name", first_name, max_len=50)
        self.last_name = require_str("last_name", last_name, max_len=50)
        self.email = require_email(email)
        self.password   = require_str("password", password, max_len=128)
        self.is_admin = require_bool("is_admin", is_admin)

    def validate(self) -> None:
        # Useful if you call update() then validate()
        self.first_name = require_str("first_name", self.first_name, max_len=50)
        self.last_name = require_str("last_name", self.last_name, max_len=50)
        self.email = require_email(self.email)
        self.is_admin = require_bool("is_admin", self.is_admin)

    def update(self, data: dict) -> None:
        if "first_name" in data:
            self.first_name = require_str("first_name", data["first_name"], max_len=50)
        if "last_name" in data:
            self.last_name = require_str("last_name", data["last_name"], max_len=50)
        if "email" in data:
            self.email = require_email(data["email"])
        if "password" in data:
            self.password = require_str("password", data["password"], max_len=128)
        if "is_admin" in data:
            self.is_admin = require_bool("is_admin", data["is_admin"])
        super().update(data)
        self.validate()
