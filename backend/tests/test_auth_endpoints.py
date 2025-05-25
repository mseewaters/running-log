# tests/test_auth_endpoints.py
"""Test authentication API endpoints using TDD methodology"""

import pytest
import os
import sys
import boto3
import jwt
from moto import mock_aws
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    @mock_aws
    def test_post_auth_register_creates_user_and_returns_jwt(self):
        """Test POST /auth/register creates user and returns JWT token - RED TEST"""
        # ARRANGE - Set up environment and mock services
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = "test-users-auth-register"
        os.environ["RUNS_TABLE"] = "test-runs-auth"
        os.environ["TARGETS_TABLE"] = "test-targets-auth"
        os.environ["JWT_SECRET"] = "test-secret"

        # Force module reload
        modules_to_reload = [
            "src.runs.app",
            "src.runs.auth.cognito_service",
            "src.runs.dal.user_dal",
            "src.runs.models.user",
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        # Create mock Cognito User Pool
        cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
        user_pool = cognito_client.create_user_pool(
            PoolName="TestPool",
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": False,
                }
            },
            UsernameAttributes=["email"],
        )
        user_pool_id = user_pool["UserPool"]["Id"]

        client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName="TestClient"
        )
        client_id = client_response["UserPoolClient"]["ClientId"]

        # Update environment with real IDs
        os.environ["COGNITO_USER_POOL_ID"] = user_pool_id
        os.environ["COGNITO_CLIENT_ID"] = client_id

        # Create mock DynamoDB tables
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # User table for synchronization
        user_table = dynamodb.create_table(
            TableName="test-users-auth-register",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Import app after environment setup
        from src.runs.app import app

        client = TestClient(app)

        # Test data
        registration_data = {
            "email": "newuser@example.com",
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User",
        }

        # ACT - Call registration endpoint (THIS WILL FAIL - endpoint doesn't exist yet)
        response = client.post("/auth/register", json=registration_data)

        # ASSERT - Should create user and return JWT token
        assert response.status_code == 201
        response_data = response.json()

        # Should return JWT token and user info
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"
        assert "user_id" in response_data
        assert response_data["email"] == "newuser@example.com"

        # JWT token should be valid and contain user ID
        token = response_data["access_token"]
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded["sub"] == response_data["user_id"]
        assert decoded["email"] == "newuser@example.com"

        # User should exist in both Cognito and DynamoDB
        cognito_users = cognito_client.list_users(UserPoolId=user_pool_id)
        assert len(cognito_users["Users"]) == 1

        # User should exist in User table
        from src.runs.dal.user_dal import get_user_by_email

        db_user = get_user_by_email("newuser@example.com")
        assert db_user is not None
        assert db_user.user_id == response_data["user_id"]

    @mock_aws
    def test_post_auth_login_authenticates_existing_user(self):
        """Test POST /auth/login authenticates existing user and returns JWT - RED TEST"""
        # ARRANGE - Set up environment and mock services
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = "test-users-auth-login"
        os.environ["RUNS_TABLE"] = "test-runs-auth"
        os.environ["TARGETS_TABLE"] = "test-targets-auth"
        os.environ["JWT_SECRET"] = "test-secret"

        # Force module reload
        modules_to_reload = [
            "src.runs.app",
            "src.runs.auth.cognito_service",
            "src.runs.dal.user_dal",
            "src.runs.models.user",
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        # Create mock Cognito User Pool
        cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
        user_pool = cognito_client.create_user_pool(
            PoolName="TestPool",
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": False,
                }
            },
            UsernameAttributes=["email"],
        )
        user_pool_id = user_pool["UserPool"]["Id"]

        client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName="TestClient"
        )
        client_id = client_response["UserPoolClient"]["ClientId"]

        # Update environment with real IDs
        os.environ["COGNITO_USER_POOL_ID"] = user_pool_id
        os.environ["COGNITO_CLIENT_ID"] = client_id

        # Create mock DynamoDB User table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        user_table = dynamodb.create_table(
            TableName="test-users-auth-login",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Import app after environment setup
        from src.runs.app import app

        client = TestClient(app)

        # FIRST: Register a user to login with
        registration_data = {
            "email": "loginuser@example.com",
            "password": "LoginUser123!",
            "first_name": "Login",
            "last_name": "User",
        }
        register_response = client.post("/auth/register", json=registration_data)
        assert register_response.status_code == 201  # Ensure registration worked

        # NOW: Test login
        login_data = {"email": "loginuser@example.com", "password": "LoginUser123!"}

        # ACT - Call login endpoint (THIS WILL FAIL - endpoint doesn't exist yet)
        response = client.post("/auth/login", json=login_data)

        # ASSERT - Should authenticate and return JWT token
        assert response.status_code == 200
        response_data = response.json()

        # Should return JWT token and user info
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"
        assert "user_id" in response_data
        assert response_data["email"] == "loginuser@example.com"

        # JWT token should be valid and contain user ID
        token = response_data["access_token"]
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded["sub"] == response_data["user_id"]
        assert decoded["email"] == "loginuser@example.com"

    @mock_aws
    def test_post_auth_login_rejects_invalid_credentials(self):
        """Test POST /auth/login rejects invalid credentials"""
        # ARRANGE - Same setup as login test
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = "test-users-auth-invalid"
        os.environ["RUNS_TABLE"] = "test-runs-auth"
        os.environ["TARGETS_TABLE"] = "test-targets-auth"
        os.environ["JWT_SECRET"] = "test-secret"

        # Force module reload
        modules_to_reload = ["src.runs.app", "src.runs.auth.cognito_service"]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        # Create mock Cognito User Pool (needed for authentication attempt)
        cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
        user_pool = cognito_client.create_user_pool(
            PoolName="TestPool",
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": False,
                }
            },
            UsernameAttributes=["email"],
        )
        user_pool_id = user_pool["UserPool"]["Id"]

        client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName="TestClient"
        )
        client_id = client_response["UserPoolClient"]["ClientId"]

        # Update environment with real IDs
        os.environ["COGNITO_USER_POOL_ID"] = user_pool_id
        os.environ["COGNITO_CLIENT_ID"] = client_id

        from src.runs.app import app

        client = TestClient(app)

        # Test data with wrong credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
        }

        # ACT - Try to login with invalid credentials
        response = client.post("/auth/login", json=login_data)

        # ASSERT - Should reject with 401
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
