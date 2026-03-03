# app/models/validators.py
from __future__ import annotations

import re
from typing import Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_str(name: str, value: Any, max_len: int | None = None) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    v = value.strip()
    if v == "":
        raise ValueError(f"{name} is required")
    if max_len is not None and len(v) > max_len:
        raise ValueError(f"{name} must be at most {max_len} characters")
    return v


def optional_str(name: str, value: Any, max_len: int | None = None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    v = value.strip()
    if v == "":
        return None
    if max_len is not None and len(v) > max_len:
        raise ValueError(f"{name} must be at most {max_len} characters")
    return v


def require_email(value: Any) -> str:
    v = require_str("email", value, max_len=None)
    if not EMAIL_RE.match(v):
        raise ValueError("email must be a valid email address")
    return v


def require_bool(name: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")
    return value


def require_float(name: str, value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    return float(value)


def require_int(name: str, value: Any) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value
