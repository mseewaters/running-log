# tests/test_user_synchronization.py
"""Test user synchronization flow between Cognito and DynamoDB"""

import pytest
import os
import boto3
import sys
from moto import mock_aws


class TestUserSynchronizationFlow:
    """Test that user registration synchronizes between Cognito and User table"""

    @mock_aws
    def test_cognito_service_creates_user_in_both_cognito_and_database(self):
        """Test that CognitoService.register_user creates user in BOTH Cognito AND User table - RED TEST"""
        # ARRANGE - Set up environment and mock services
        os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_TestPool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["USERS_TABLE"] = "test-users-sync"

        # Force module reload
        modules_to_reload = [
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

        # Create user pool client
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
            TableName="test-users-sync",
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

        # Import services after environment setup
        from src.runs.auth.cognito_service import CognitoService
        from src.runs.dal.user_dal import get_user_by_email

        cognito_service = CognitoService()

        # Test data
        user_data = {
            "email": "sync-test@example.com",
            "password": "SyncPass123!",
            "first_name": "Sync",
            "last_name": "Test",
        }

        # ACT - Register user (should create in BOTH Cognito AND User table)
        result = cognito_service.register_user(user_data)

        # ASSERT - User created successfully
        assert result["success"] is True
        assert "user_id" in result
        cognito_user_id = result["user_id"]

        # VERIFY - User exists in Cognito
        cognito_users = cognito_client.list_users(UserPoolId=user_pool_id)
        assert len(cognito_users["Users"]) == 1

        # VERIFY - User also exists in DynamoDB User table (THIS WILL FAIL initially)
        # This is what we need to implement!
        db_user = get_user_by_email("sync-test@example.com")
        assert db_user is not None, "User should be created in DynamoDB User table"
        assert db_user.user_id == cognito_user_id, "User table should use Cognito UUID"
        assert db_user.email == "sync-test@example.com"
        assert db_user.first_name == "Sync"
        assert db_user.last_name == "Test"
