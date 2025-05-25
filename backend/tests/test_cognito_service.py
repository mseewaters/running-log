# tests/test_cognito_service.py
"""Test Cognito service layer using TDD methodology"""

import pytest
import os
from moto import mock_aws
import boto3


class TestCognitoService:
    """Test Cognito service operations"""

    @mock_aws
    def test_cognito_service_can_register_user(self):
        """Test that we can register a new user through Cognito service"""
        # ARRANGE - Set up mock Cognito User Pool (like the working test)
        import boto3

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

        # Create user pool client
        client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName="TestClient"
        )
        client_id = client_response["UserPoolClient"]["ClientId"]

        # Set environment variables to point to our mock pool
        os.environ["COGNITO_USER_POOL_ID"] = user_pool_id
        os.environ["COGNITO_CLIENT_ID"] = client_id
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = "test-users-cognito"  # Add this for User table sync

        # FORCE MODULE RELOAD to pick up new environment variables
        import sys

        modules_to_reload = [
            "src.runs.auth.cognito_service",
            "src.runs.dal.user_dal",
            "src.runs.models.user",
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        # Create mock User table for synchronization
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        user_table = dynamodb.create_table(
            TableName="test-users-cognito",
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

        from src.runs.auth.cognito_service import CognitoService

        cognito_service = CognitoService()

        # Test data
        user_data = {
            "email": "test@example.com",
            "password": "TempPass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        # ACT & ASSERT - This should now pass with real mock Cognito
        result = cognito_service.register_user(user_data)

        # DEBUG - Let's see what error we're getting
        print(f"Result: {result}")

        assert result["success"] is True
        assert "user_id" in result

    @mock_aws
    def test_cognito_service_validates_email_format(self):
        """Test that CognitoService validates email format"""
        # ARRANGE
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"

        from src.runs.auth.cognito_service import CognitoService

        cognito_service = CognitoService()

        # Test data with invalid email
        user_data = {
            "email": "not-an-email",  # Invalid email format
            "password": "TempPass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        # ACT & ASSERT - This should fail our current implementation
        result = cognito_service.register_user(user_data)
        assert result["success"] is False
        assert "error" in result
        assert "email" in result["error"].lower()

    @mock_aws
    def test_cognito_service_validates_password_requirements(self):
        """Test that CognitoService validates password requirements"""
        # ARRANGE
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"

        from src.runs.auth.cognito_service import CognitoService

        cognito_service = CognitoService()

        # Test data with weak password
        user_data = {
            "email": "test@example.com",  # Valid email
            "password": "weak",  # Invalid password (too short, no uppercase/numbers)
            "first_name": "John",
            "last_name": "Doe",
        }

        # ACT & ASSERT - This should fail our current implementation
        result = cognito_service.register_user(user_data)
        assert result["success"] is False
        assert "error" in result
        assert "password" in result["error"].lower()

    @mock_aws
    def test_cognito_service_actually_creates_user_in_cognito(self):
        """Test that CognitoService actually creates user in mocked Cognito"""
        # ARRANGE - Set up mock Cognito User Pool using moto
        import boto3
        from moto import mock_aws

        # Create mock Cognito User Pool
        cognito_client = boto3.client("cognito-idp", region_name="us-east-1")

        # Create a real mock user pool
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

        # Create user pool client
        client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id, ClientName="TestClient"
        )
        client_id = client_response["UserPoolClient"]["ClientId"]

        # Set environment variables to point to our mock pool
        os.environ["COGNITO_USER_POOL_ID"] = user_pool_id
        os.environ["COGNITO_CLIENT_ID"] = client_id
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = (
            "test-users-cognito-real"  # Add this for User table sync
        )

        # FORCE MODULE RELOAD to pick up new environment variables
        import sys

        modules_to_reload = [
            "src.runs.auth.cognito_service",
            "src.runs.dal.user_dal",
            "src.runs.models.user",
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        # Create mock User table for synchronization
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        user_table = dynamodb.create_table(
            TableName="test-users-cognito-real",
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

        from src.runs.auth.cognito_service import CognitoService

        cognito_service = CognitoService()

        # Test data
        user_data = {
            "email": "real-test@example.com",
            "password": "RealPass123!",
            "first_name": "Jane",
            "last_name": "Smith",
        }

        # ACT & ASSERT - This should create a REAL user in mock Cognito
        result = cognito_service.register_user(user_data)
        assert result["success"] is True
        assert "user_id" in result

        # VERIFY - Check that user was actually created in mock Cognito
        users_response = cognito_client.list_users(UserPoolId=user_pool_id)
        assert len(users_response["Users"]) == 1

        # Check that the user has the correct email attribute (not necessarily username)
        created_user = users_response["Users"][0]
        user_attributes = {
            attr["Name"]: attr["Value"] for attr in created_user["Attributes"]
        }
        assert user_attributes["email"] == "real-test@example.com"
