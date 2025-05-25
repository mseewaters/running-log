# src/auth/cognito_service.py
"""Cognito service for user authentication - with REAL Cognito integration"""

import os
import re
import boto3
from botocore.exceptions import ClientError


class CognitoService:
    """Service for handling Cognito user operations"""

    def __init__(self):
        """Initialize Cognito service with environment configuration"""
        self.user_pool_id = os.environ.get("COGNITO_USER_POOL_ID")
        self.client_id = os.environ.get("COGNITO_CLIENT_ID")
        self.region = os.environ.get("AWS_REGION", "us-east-1")

        # Initialize boto3 Cognito client
        self.cognito_client = boto3.client("cognito-idp", region_name=self.region)

    def _validate_email(self, email):
        """Validate email format using regex"""
        if not email:
            return False

        # Basic email regex pattern (same as in your User model)
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _validate_password(self, password):
        """Validate password meets requirements"""
        if not password:
            return False

        # Password requirements (matching Cognito User Pool policy from template)
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):  # Requires uppercase
            return False
        if not re.search(r"[a-z]", password):  # Requires lowercase
            return False
        if not re.search(r"[0-9]", password):  # Requires numbers
            return False

        return True

    def register_user(self, user_data):
        """Register a new user with REAL Cognito integration AND User table synchronization"""
        # Validate email first
        email = user_data.get("email", "")
        if not self._validate_email(email):
            return {"success": False, "error": "Invalid email format"}

        # Validate password
        password = user_data.get("password", "")
        if not self._validate_password(password):
            return {"success": False, "error": "Invalid password format"}

        # REAL Cognito integration - create user in Cognito User Pool
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,  # Use email as username
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "given_name", "Value": user_data.get("first_name", "")},
                    {"Name": "family_name", "Value": user_data.get("last_name", "")},
                    {
                        "Name": "email_verified",
                        "Value": "true",  # Auto-verify for testing
                    },
                ],
                TemporaryPassword=password,
                MessageAction="SUPPRESS",  # Don't send welcome email in tests
            )

            # Set permanent password (bypass temporary password requirement)
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=password,
                Permanent=True,
            )

            # NEW: SYNCHRONIZATION - Also create user in User table
            cognito_user_id = response["User"]["Username"]  # Cognito's UUID

            # Import User model and DAL (after Cognito success)
            try:
                from models.user import User
                from dal.user_dal import save_user
            except ImportError:
                from ..models.user import User
                from ..dal.user_dal import save_user

            # Create User model with Cognito UUID
            user = User(
                user_id=cognito_user_id,  # Use Cognito's UUID
                email=email,
                password_hash="cognito_managed",  # Cognito manages password
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
            )

            # Save to DynamoDB User table
            save_user(user)

            return {
                "success": True,
                "user_id": cognito_user_id,
                "cognito_user_id": cognito_user_id,
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            return {
                "success": False,
                "error": f"Cognito error: {error_code} - {error_message}",
            }
        except Exception as e:
            # Handle any User table creation errors
            return {"success": False, "error": f"User synchronization error: {str(e)}"}

    def authenticate_user(self, email, password):
        """Authenticate an existing user with Cognito"""
        try:
            # Use Cognito's admin_initiate_auth for authentication
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password},
            )

            # If we get here, authentication succeeded
            # Get user details from the auth result
            access_token = response["AuthenticationResult"]["AccessToken"]

            # Get user info using the access token
            user_info = self.cognito_client.get_user(AccessToken=access_token)

            # Extract user ID from user attributes
            user_id = user_info["Username"]  # This is the Cognito UUID

            # Get email from user attributes
            user_email = None
            for attr in user_info["UserAttributes"]:
                if attr["Name"] == "email":
                    user_email = attr["Value"]
                    break

            return {
                "success": True,
                "user_id": user_id,
                "email": user_email or email,
                "access_token": access_token,
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            # Handle specific authentication errors
            if error_code in ["NotAuthorizedException", "UserNotFoundException"]:
                return {"success": False, "error": "Invalid email or password"}
            else:
                return {
                    "success": False,
                    "error": f"Authentication error: {error_code}",
                }
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
