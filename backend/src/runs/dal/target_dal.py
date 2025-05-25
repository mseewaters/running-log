"""Target Data Access Layer - handles saving/loading targets from DynamoDB"""

import boto3
import os
from decimal import Decimal
from datetime import datetime

try:
    from models.target import Target
except ImportError:
    from ..models.target import Target


def _get_table():
    """Get the DynamoDB table for targets"""
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("TARGETS_TABLE", "test-targets")
    return dynamodb.Table(table_name)


def save_target(target):
    """Save a target to DynamoDB"""
    table = _get_table()

    item = {
        "user_id": target.user_id,
        "target_id": target.target_id,
        "target_type": target.target_type,
        "period": target.period,
        "distance_km": target.distance_km,
        "created_at": target.created_at.isoformat(),
    }

    table.put_item(Item=item)


def get_targets_by_user(user_id):
    """Get all targets for a specific user"""
    table = _get_table()

    response = table.query(
        KeyConditionExpression="user_id = :user_id",
        ExpressionAttributeValues={":user_id": user_id},
    )

    targets = []
    for item in response.get("Items", []):
        target = Target(
            user_id=item["user_id"],
            target_type=item["target_type"],
            period=item["period"],
            distance_km=item["distance_km"],
        )

        # Override auto-generated values with stored ones
        target.target_id = item["target_id"]
        target.created_at = datetime.fromisoformat(item["created_at"])
        targets.append(target)

    return targets
