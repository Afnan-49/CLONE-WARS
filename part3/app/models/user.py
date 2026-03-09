from app.models.base_model import BaseModel
import re

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = self.validate_string(first_name, "First name")
        self.last_name = self.validate_string(last_name, "Last name")
        self.email = self.validate_email(email)
        self.password = password  # This should be the hashed password
        self.is_admin = is_admin  # NEW: Field for Role-Based Access

    def validate_string(self, value, field_name):
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} must be a non-empty string.")
        return value

    def validate_email(self, email):
        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format.")
        return email

    def to_dict(self):
        """Return a dictionary representation of the user"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
