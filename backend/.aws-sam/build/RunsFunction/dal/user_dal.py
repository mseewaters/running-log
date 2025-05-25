"""User Data Access Layer - handles saving/loading users from DynamoDB"""

import boto3
import os
from decimal import Decimal
from datetime import datetime

try:
    from models.user import User
except ImportError:
    from ..models.user import User


def _get_table():
    """Get the DynamoDB table for users"""
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("USERS_TABLE", "test-users")
    return dynamodb.Table(table_name)


def save_user(user):
    """Save a user to DynamoDB"""
    table = _get_table()

    item = {
        "user_id": user.user_id,
        "email": user.email,
        "password_hash": user.password_hash,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat(),
    }

    table.put_item(Item=item)


def get_user_by_id(user_id):
    """Get a user by their user_id"""
    table = _get_table()

    response = table.get_item(Key={"user_id": user_id})
    item = response.get("Item")

    if not item:
        return None

    # Convert DynamoDB item back to User model
    user = User(
        email=item["email"],
        password_hash=item["password_hash"],
        first_name=item["first_name"],
        last_name=item["last_name"],
    )
    # Override the auto-generated values with stored ones
    user.user_id = item["user_id"]
    user.created_at = datetime.fromisoformat(item["created_at"])

    return user


def get_user_by_email(email):
    """Get a user by their email address"""
    table = _get_table()

    # Query the email GSI
    response = table.query(
        IndexName="email-index",
        KeyConditionExpression="email = :email",
        ExpressionAttributeValues={":email": email},
    )

    items = response.get("Items", [])
    if not items:
        return None

    # Take the first match (should be unique)
    item = items[0]

    user = User(
        email=item["email"],
        password_hash=item["password_hash"],
        first_name=item["first_name"],
        last_name=item["last_name"],
    )
    user.user_id = item["user_id"]
    user.created_at = datetime.fromisoformat(item["created_at"])

    return user
