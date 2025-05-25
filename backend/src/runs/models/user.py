import uuid
import re
from datetime import datetime
from typing import Optional


class User:
    def __init__(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        user_id: str = None,
    ):
        # Validate email format before storing
        self._validate_email(email)

        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name

        # Use provided user_id (e.g., from Cognito) or generate new one
        self.user_id = user_id if user_id is not None else str(uuid.uuid4())
        self.created_at = datetime.utcnow()

    def _validate_email(self, email: str) -> None:
        """Validate email format using regex"""
        if not email:
            raise ValueError("Invalid email format")

        # Basic email regex pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, email):
            raise ValueError("Invalid email format")

    @property
    def full_name(self) -> str:
        """Return full name for display purposes"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"User(user_id='{self.user_id}', email='{self.email}', name='{self.full_name}')"
