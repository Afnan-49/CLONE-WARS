# app/models/base_model.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict


class BaseModel:
    def __init__(self) -> None:
        self.id: str = str(uuid.uuid4())
        now = datetime.utcnow()
        self.created_at: datetime = now
        self.updated_at: datetime = now

    def save(self) -> None:
        self.updated_at = datetime.utcnow()

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update allowed attributes from a dict and refresh updated_at.
        Child classes should validate after calling this (or override).
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
