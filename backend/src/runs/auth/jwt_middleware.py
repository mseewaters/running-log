# src/auth/jwt_middleware.py
"""JWT authentication middleware for extracting user IDs from tokens"""

import jwt
from datetime import datetime


def extract_user_id_from_token(token: str, secret: str) -> str:
    """
    Extract user ID from JWT token

    Args:
        token: JWT token string
        secret: Secret key for token verification

    Returns:
        User ID (sub claim) if token is valid, None otherwise
    """
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Extract user ID from 'sub' claim (standard JWT claim for subject/user ID)
        user_id = payload.get("sub")

        return user_id

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None

    except jwt.InvalidTokenError:
        # Token is invalid (malformed, wrong signature, etc.)
        return None

    except Exception:
        # Any other error
        return None
