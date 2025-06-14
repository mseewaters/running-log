# backend/tests/test_target_api.py
"""Test target API endpoints using TDD methodology - based on working test_api.py framework"""

import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
import os
import sys
import jwt
from datetime import date, datetime, timedelta
import json


@pytest.fixture
def auth_headers():
    """Create valid JWT token for authentication"""
    payload = {
        "sub": "test-user-123",  # User ID
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_dynamodb():
    with mock_aws():
        # Set environment variables FIRST, before any imports
        os.environ["RUNS_TABLE"] = "test-runs"
        os.environ["USERS_TABLE"] = "test-users"
        os.environ["TARGETS_TABLE"] = "test-targets-enhanced"
        os.environ["JWT_SECRET"] = "test-secret"  # CRITICAL: Set this early

        # FORCE MODULE RELOAD to pick up new environment variables
        modules_to_reload = [
            "src.runs.app",
            "src.runs.dal.target_dal",
            "src.runs.models.target",
            "src.runs.auth.jwt_middleware",
        ]

        for module_name in modules_to_reload:
            if module_name in sys.modules:
                del sys.modules[module_name]

        # Create mock DynamoDB tables
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create Targets table (main table for this test)
        targets_table = dynamodb.create_table(
            TableName="test-targets-enhanced",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "target_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "target_id", "AttributeType": "S"},
                {"AttributeName": "period", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user-period-index",
                    "KeySchema": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "period", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield dynamodb


def test_create_monthly_target_success(mock_dynamodb, auth_headers):
    """Test creating a monthly target successfully"""
    from src.runs.app import app

    client = TestClient(app)

    # Valid monthly target request
    target_data = {"target_type": "monthly", "period": "2025-06", "distance_km": 100.0}

    response = client.post("/targets", json=target_data, headers=auth_headers)

    # Should create successfully
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["target_type"] == "monthly"
    assert response_data["period"] == "2025-06"
    assert response_data["distance_km"] == 100.0
    assert response_data["user_id"] == "test-user-123"
    assert "target_id" in response_data
    assert "created_at" in response_data


def test_create_yearly_target_success(mock_dynamodb, auth_headers):
    """Test creating a yearly target successfully"""
    from src.runs.app import app

    client = TestClient(app)

    # Valid yearly target request
    target_data = {"target_type": "yearly", "period": "2025", "distance_km": 1200.0}

    response = client.post("/targets", json=target_data, headers=auth_headers)

    # Should create successfully
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["target_type"] == "yearly"
    assert response_data["period"] == "2025"
    assert response_data["distance_km"] == 1200.0


def test_create_target_validation_errors(mock_dynamodb, auth_headers):
    """Test target creation with invalid data"""
    from src.runs.app import app

    client = TestClient(app)

    # Test invalid target type
    invalid_data = {
        "target_type": "weekly",  # Invalid type
        "period": "2025-06",
        "distance_km": 100.0,
    }

    response = client.post("/targets", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422

    # Test invalid monthly period format
    invalid_data = {
        "target_type": "monthly",
        "period": "2025-13",  # Invalid month
        "distance_km": 100.0,
    }

    response = client.post("/targets", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422

    # Test negative distance
    invalid_data = {
        "target_type": "monthly",
        "period": "2025-06",
        "distance_km": -10.0,  # Invalid negative distance
    }

    response = client.post("/targets", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422


def test_get_targets_for_user(mock_dynamodb, auth_headers):
    """Test getting all targets for a user"""
    from src.runs.app import app

    client = TestClient(app)

    # Create a couple of targets first
    target1 = {"target_type": "monthly", "period": "2025-06", "distance_km": 100.0}

    target2 = {"target_type": "yearly", "period": "2025", "distance_km": 1200.0}

    # Create targets
    client.post("/targets", json=target1, headers=auth_headers)
    client.post("/targets", json=target2, headers=auth_headers)

    # Get all targets
    response = client.get("/targets", headers=auth_headers)

    assert response.status_code == 200
    targets = response.json()

    # Should return both targets
    assert len(targets) == 2
    assert targets[0]["user_id"] == "test-user-123"
    assert targets[1]["user_id"] == "test-user-123"


def test_get_targets_empty_list(mock_dynamodb, auth_headers):
    """Test getting targets when user has none"""
    from src.runs.app import app

    client = TestClient(app)

    response = client.get("/targets", headers=auth_headers)

    assert response.status_code == 200
    targets = response.json()
    assert targets == []


def test_targets_require_authentication(mock_dynamodb):
    """Test that target endpoints require authentication"""
    from src.runs.app import app

    client = TestClient(app)

    # Test POST without authentication
    target_data = {"target_type": "monthly", "period": "2025-06", "distance_km": 100.0}

    response = client.post("/targets", json=target_data)
    assert response.status_code == 403

    # Test GET without authentication
    response = client.get("/targets")
    assert response.status_code == 403


def test_target_period_display_format(mock_dynamodb, auth_headers):
    """Test that targets return proper period display format"""
    from src.runs.app import app

    client = TestClient(app)

    # Create monthly target
    monthly_target = {
        "target_type": "monthly",
        "period": "2025-06",
        "distance_km": 100.0,
    }

    response = client.post("/targets", json=monthly_target, headers=auth_headers)
    assert response.status_code == 201

    target = response.json()
    # Should include period_display for frontend
    assert "period_display" in target
    assert target["period_display"] == "June 2025"

    # Create yearly target
    yearly_target = {"target_type": "yearly", "period": "2025", "distance_km": 1200.0}

    response = client.post("/targets", json=yearly_target, headers=auth_headers)
    target = response.json()
    assert target["period_display"] == "2025"


def test_create_target_overwrites_existing_target(mock_dynamodb, auth_headers):
    """Test that creating a target for existing period overwrites the old target"""
    from src.runs.app import app

    client = TestClient(app)

    # ARRANGE - Create initial target
    initial_target = {
        "target_type": "monthly",
        "period": "2025-06",
        "distance_km": 100.0,
    }

    # ACT - Create first target
    response1 = client.post("/targets", json=initial_target, headers=auth_headers)
    assert response1.status_code == 201
    first_target_data = response1.json()

    # ARRANGE - Create updated target for same period
    updated_target = {
        "target_type": "monthly",
        "period": "2025-06",  # Same period
        "distance_km": 150.0,  # Different distance
    }

    # ACT - Create second target for same period (should overwrite)
    response2 = client.post("/targets", json=updated_target, headers=auth_headers)
    assert response2.status_code == 201
    second_target_data = response2.json()

    # ASSERT - Should return the updated distance
    assert second_target_data["distance_km"] == 150.0
    assert second_target_data["period"] == "2025-06"

    # ASSERT - Get all targets and verify only one exists for this period
    get_response = client.get("/targets", headers=auth_headers)
    assert get_response.status_code == 200
    targets = get_response.json()

    # Filter targets for the test period
    june_targets = [t for t in targets if t["period"] == "2025-06"]

    # Should only have ONE target for June 2025
    assert len(june_targets) == 1
    assert june_targets[0]["distance_km"] == 150.0  # Should be the updated value
    assert (
        june_targets[0]["target_id"] != first_target_data["target_id"]
    )  # Should be different target_id
