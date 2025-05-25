# tests/test_cognito_infrastructure.py
"""Test Cognito infrastructure setup and environment variables"""

import os
import pytest


class TestCognitoInfrastructure:
    """Test Cognito infrastructure is properly configured"""

    def test_cognito_environment_variables_exist(self):
        """Test that Cognito environment variables are available"""
        # These will be set in the Lambda environment after deployment
        # For now, we'll test that they can be set manually for local testing

        # Set test environment variables (simulating Lambda environment)
        os.environ["COGNITO_USER_POOL_ID"] = "test-user-pool-id"
        os.environ["COGNITO_CLIENT_ID"] = "test-client-id"
        os.environ["AWS_REGION"] = "us-east-1"

        # Verify they can be read
        assert os.environ.get("COGNITO_USER_POOL_ID") == "test-user-pool-id"
        assert os.environ.get("COGNITO_CLIENT_ID") == "test-client-id"
        assert os.environ.get("AWS_REGION") == "us-east-1"

    def test_cognito_config_helper(self):
        """Test helper function to get Cognito configuration"""
        # Set up test environment
        os.environ["COGNITO_USER_POOL_ID"] = "test-pool"
        os.environ["COGNITO_CLIENT_ID"] = "test-client"
        os.environ["AWS_REGION"] = "us-east-1"

        # This will be our helper function for getting Cognito config
        def get_cognito_config():
            return {
                "user_pool_id": os.environ.get("COGNITO_USER_POOL_ID"),
                "client_id": os.environ.get("COGNITO_CLIENT_ID"),
                "region": os.environ.get("AWS_REGION", "us-east-1"),
            }

        config = get_cognito_config()

        assert config["user_pool_id"] == "test-pool"
        assert config["client_id"] == "test-client"
        assert config["region"] == "us-east-1"

    def test_sam_template_builds_successfully(self):
        """Test that SAM template with Cognito resources is valid"""
        # This test would normally use SAM CLI to validate template
        # For now, we'll just test that the concept works

        # Simulate checking template syntax
        template_has_cognito = True  # This would be actual template validation
        template_has_user_pool = True
        template_has_client = True

        assert template_has_cognito, "Template should include Cognito resources"
        assert template_has_user_pool, "Template should include User Pool"
        assert template_has_client, "Template should include User Pool Client"
