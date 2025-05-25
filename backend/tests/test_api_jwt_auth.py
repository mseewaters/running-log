# tests/test_api_jwt_auth.py
"""Test API endpoints with JWT authentication"""

import pytest
import os
import jwt
from moto import mock_aws
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


@mock_aws
class TestAPIJWTAuthentication:
    """Test API endpoints require and use JWT authentication"""

    def test_runs_endpoint_requires_authorization_header(self):
        """Test that /runs endpoint requires Authorization header"""
        # ARRANGE - Set up mock DynamoDB tables
        import boto3

        # Create mock DynamoDB tables (like in other tests)
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create Runs table
        runs_table = dynamodb.create_table(
            TableName="test-runs",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        os.environ["RUNS_TABLE"] = "test-runs"
        os.environ["USERS_TABLE"] = "test-users"
        os.environ["TARGETS_TABLE"] = "test-targets"
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"

        from src.runs.app import app

        client = TestClient(app)

        # ACT - Request without Authorization header
        response = client.get("/runs")

        # ASSERT - FastAPI HTTPBearer returns 403 for missing auth
        assert response.status_code == 403
        assert "not authenticated" in response.json()["detail"].lower()

    def test_runs_endpoint_should_require_jwt_authentication(self):
        """Test that /runs endpoint should require JWT authentication - REAL RED TEST"""
        # ARRANGE - Set up mock DynamoDB tables
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        runs_table = dynamodb.create_table(
            TableName="test-runs-auth",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        os.environ["RUNS_TABLE"] = "test-runs-auth"
        os.environ["JWT_SECRET"] = "test-secret"

        from src.runs.app import app

        client = TestClient(app)

        # ACT - Request without Authorization header
        response = client.get("/runs")

        # ASSERT - FastAPI HTTPBearer returns 403 for missing auth, not 401
        assert (
            response.status_code == 403
        ), f"Expected 403 (not authenticated), got {response.status_code}"
        assert "not authenticated" in response.json()["detail"].lower()

    def test_runs_endpoint_accepts_valid_jwt_token(self):
        """Test that /runs endpoint works with valid JWT token"""
        # FIX: Set environment variables BEFORE importing app
        os.environ["RUNS_TABLE"] = "test-runs-valid"
        os.environ["USERS_TABLE"] = "test-users"
        os.environ["TARGETS_TABLE"] = "test-targets"
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["JWT_SECRET"] = "test-secret"

        # FORCE MODULE RELOAD to pick up new environment variables
        import sys

        if "src.runs.app" in sys.modules:
            del sys.modules["src.runs.app"]
        if "src.runs.dal.run_dal" in sys.modules:
            del sys.modules["src.runs.dal.run_dal"]

        # DEBUG - Let's see the environment when run with other tests
        print(f"RUNS_TABLE: {os.environ.get('RUNS_TABLE')}")
        print(f"JWT_SECRET: {os.environ.get('JWT_SECRET')}")

        # ARRANGE
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        runs_table = dynamodb.create_table(
            TableName="test-runs-valid",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Create valid JWT token
        payload = {
            "sub": "c968c7c0-9b75-4a1e-8b2c-616e9715ec56",  # User ID
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")

        # Import AFTER setting environment and clearing cache
        from src.runs.app import app

        client = TestClient(app)

        # ACT - Request with valid Authorization header
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/runs", headers=headers)

        # DEBUG - Let's see what we're getting
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")

        # ASSERT - Should work and return empty runs list
        assert response.status_code == 200
        assert response.json() == []

    def test_runs_endpoint_rejects_invalid_jwt_token(self):
        """Test that /runs endpoint rejects invalid JWT tokens"""
        # ARRANGE
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        runs_table = dynamodb.create_table(
            TableName="test-runs-invalid",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        os.environ["RUNS_TABLE"] = "test-runs-invalid"
        os.environ["USERS_TABLE"] = "test-users"
        os.environ["TARGETS_TABLE"] = "test-targets"
        os.environ["JWT_SECRET"] = "test-secret"

        from src.runs.app import app

        client = TestClient(app)

        # ACT - Request with invalid token
        headers = {"Authorization": "Bearer invalid.jwt.token"}
        response = client.get("/runs", headers=headers)

        # ASSERT - Should reject with 401 (our custom error for invalid tokens)
        assert response.status_code == 401
        assert "invalid or expired" in response.json()["detail"].lower()
