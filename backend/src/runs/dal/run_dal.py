"""Run Data Access Layer - handles saving/loading runs from DynamoDB"""

import boto3
import os
from decimal import Decimal
from datetime import datetime, date

try:
    from models.run import Run
except ImportError:
    from ..models.run import Run


def _get_table():
    """Get the DynamoDB table for runs"""
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("RUNS_TABLE", "test-runs")
    return dynamodb.Table(table_name)


def save_run(run):
    """Save a run to DynamoDB"""
    table = _get_table()

    item = {
        "user_id": run.user_id,
        "run_id": run.run_id,
        "date": run.date.isoformat(),  # Store as YYYY-MM-DD string
        "distance_km": run.distance_km,
        "duration_seconds": run.duration_seconds,
        "notes": run.notes,
        "created_at": run.created_at.isoformat(),
    }

    table.put_item(Item=item)


def get_run_by_id(user_id, run_id):
    """Get a specific run by user_id and run_id"""
    table = _get_table()

    response = table.get_item(Key={"user_id": user_id, "run_id": run_id})

    item = response.get("Item")
    if not item:
        return None

    # Convert DynamoDB item back to Run model
    # We need to reconstruct the duration string from seconds
    duration_seconds = int(item["duration_seconds"])
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    run = Run(
        user_id=item["user_id"],
        date=date.fromisoformat(item["date"]),
        distance_km=item["distance_km"],
        duration=duration_str,
        notes=item.get("notes", ""),
    )

    # Override auto-generated values with stored ones
    run.run_id = item["run_id"]
    run.created_at = datetime.fromisoformat(item["created_at"])

    return run


def get_runs_by_user(user_id):
    """Get all runs for a specific user"""
    table = _get_table()

    response = table.query(
        KeyConditionExpression="user_id = :user_id",
        ExpressionAttributeValues={":user_id": user_id},
    )

    runs = []
    for item in response.get("Items", []):
        # Convert each item back to Run model
        duration_seconds = int(item["duration_seconds"])
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        run = Run(
            user_id=item["user_id"],
            date=date.fromisoformat(item["date"]),
            distance_km=item["distance_km"],
            duration=duration_str,
            notes=item.get("notes", ""),
        )

        run.run_id = item["run_id"]
        run.created_at = datetime.fromisoformat(item["created_at"])
        runs.append(run)

    return runs


def update_run_by_id(run_id, user_id, updated_run):
    """Update a specific run in DynamoDB"""
    table = _get_table()

    # Delete the old run first
    table.delete_item(
        Key={
            "user_id": user_id,
            "run_id": run_id,
        }
    )

    # Save the updated run (same as save_run but with existing run_id)
    item = {
        "user_id": updated_run.user_id,
        "run_id": updated_run.run_id,
        "date": updated_run.date.isoformat(),
        "distance_km": updated_run.distance_km,
        "duration": updated_run.duration,
        "pace": updated_run.pace,
        "notes": updated_run.notes,
        "created_at": updated_run.created_at.isoformat(),
    }

    table.put_item(Item=item)


def delete_run_by_id(run_id, user_id):
    """Delete a specific run from DynamoDB"""
    table = _get_table()

    table.delete_item(
        Key={
            "user_id": user_id,
            "run_id": run_id,
        }
    )
