# tests/test_jwt_middleware.py
"""Test JWT authentication middleware using TDD"""

import pytest
import os
from moto import mock_aws
import jwt
import json
from datetime import datetime, timedelta


class TestJWTMiddleware:
    """Test JWT token authentication and user ID extraction"""

    def test_extract_user_id_from_valid_jwt_token(self):
        """Test extracting user ID from valid JWT token - RED TEST"""
        # ARRANGE - This will fail because we haven't created the auth middleware yet

        # Mock JWT token payload (what Cognito would send)
        payload = {
            "sub": "c968c7c0-9b75-4a1e-8b2c-616e9715ec56",  # Cognito user ID
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        # Create mock JWT token
        secret = "test-secret"
        token = jwt.encode(payload, secret, algorithm="HS256")

        # This import will fail - we haven't created the auth module yet
        from src.runs.auth.jwt_middleware import extract_user_id_from_token

        # ACT & ASSERT
        user_id = extract_user_id_from_token(token, secret)
        assert user_id == "c968c7c0-9b75-4a1e-8b2c-616e9715ec56"

    def test_extract_user_id_handles_invalid_token(self):
        """Test that invalid JWT tokens are handled gracefully"""
        # ARRANGE
        invalid_token = "invalid.jwt.token"
        secret = "test-secret"

        from src.runs.auth.jwt_middleware import extract_user_id_from_token

        # ACT & ASSERT - Should return None for invalid tokens
        user_id = extract_user_id_from_token(invalid_token, secret)
        assert user_id is None

    def test_extract_user_id_handles_expired_token(self):
        """Test that expired JWT tokens are handled gracefully"""
        # ARRANGE - Create expired token
        payload = {
            "sub": "c968c7c0-9b75-4a1e-8b2c-616e9715ec56",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        }

        secret = "test-secret"
        expired_token = jwt.encode(payload, secret, algorithm="HS256")

        from src.runs.auth.jwt_middleware import extract_user_id_from_token

        # ACT & ASSERT - Should return None for expired tokens
        user_id = extract_user_id_from_token(expired_token, secret)
        assert user_id is None
