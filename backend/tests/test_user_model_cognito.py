# tests/test_user_model_cognito.py
"""Test User model integration with Cognito UUIDs"""

import pytest
from datetime import datetime


class TestUserModelCognitoIntegration:
    """Test User model works with Cognito-provided UUIDs"""

    def test_user_model_accepts_cognito_user_id(self):
        """Test that User model can accept Cognito UUID instead of generating its own - RED TEST"""
        # ARRANGE
        cognito_user_id = (
            "c968c7c0-9b75-4a1e-8b2c-616e9715ec56"  # Cognito-provided UUID
        )

        # This should fail because current User model generates its own UUID
        from src.runs.models.user import User

        # ACT - Create user with Cognito UUID
        user = User(
            user_id=cognito_user_id,  # Pass Cognito UUID as parameter
            email="test@example.com",
            password_hash="hashed_password_123",
            first_name="John",
            last_name="Doe",
        )

        # ASSERT - User should use the provided Cognito UUID, not generate its own
        assert user.user_id == cognito_user_id
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_user_model_still_generates_uuid_if_none_provided(self):
        """Test that User model still auto-generates UUID if none provided (backward compatibility)"""
        # ARRANGE & ACT - Create user without providing user_id (current behavior)
        from src.runs.models.user import User

        user = User(
            email="test2@example.com",
            password_hash="hashed_password_456",
            first_name="Jane",
            last_name="Smith",
        )

        # ASSERT - Should auto-generate UUID (existing behavior)
        assert user.user_id is not None
        assert len(user.user_id) > 10  # UUID-like string
        assert user.email == "test2@example.com"
