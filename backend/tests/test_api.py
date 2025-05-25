# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
import os
import sys
import jwt
from datetime import date, datetime, timedelta
import json

from src.runs.app import app


@pytest.fixture
def client():
    # Don't import app here - let each test import it after setting environment
    return None  # We'll create TestClient in each test


@pytest.fixture
def auth_headers():
    """Create valid JWT token for authentication"""
    # JWT secret should already be set by mock_dynamodb fixture
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
        os.environ["RUNS_TABLE"] = "test-runs-enhanced"
        os.environ["USERS_TABLE"] = "test-users"
        os.environ["TARGETS_TABLE"] = "test-targets"
        os.environ["JWT_SECRET"] = "test-secret"  # CRITICAL: Set this early

        # FORCE MODULE RELOAD to pick up new environment variables
        modules_to_reload = [
            "src.runs.app",
            "src.runs.dal.run_dal",
            "src.runs.dal.user_dal",
            "src.runs.dal.target_dal",
            "src.runs.auth.jwt_middleware",  # Add this too!
        ]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create the Runs table with the name your DAL expects
        runs_table = dynamodb.create_table(
            TableName="test-runs-enhanced",  # Match environment variable
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
                {"AttributeName": "run_date", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user-date-index",
                    "KeySchema": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "run_date", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield dynamodb


class TestEnhancedRunsAPI:

    def test_post_run_saves_to_database(self, mock_dynamodb, auth_headers):
        """Test that POST /runs saves a run to the database"""
        # Import app AFTER environment is set
        from src.runs.app import app

        client = TestClient(app)

        # Arrange
        run_data = {
            "date": "2024-01-15",
            "distance_km": 5.2,
            "duration": "00:25:30",  # Must be HH:MM:SS format for your model
            "notes": "Morning run in the park",
        }

        # Act - Include authentication headers
        response = client.post("/runs", json=run_data, headers=auth_headers)

        # Debug: Print response details if it fails
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")

        # Assert
        assert response.status_code == 201
        response_data = response.json()

        # Verify response structure
        assert "run_id" in response_data
        assert response_data["date"] == "2024-01-15"
        assert response_data["distance_km"] == 5.2
        assert response_data["duration"] == "00:25:30"
        assert response_data["pace"] == "04:54"  # Expected pace for 5.2 km in 25:30
        assert response_data["notes"] == "Morning run in the park"

        # Verify data was saved to database
        table = mock_dynamodb.Table("test-runs-enhanced")
        items = table.scan()["Items"]
        assert len(items) == 1

        saved_run = items[0]
        assert (
            float(saved_run["distance_km"]) == 5.2
        )  # Convert Decimal to float for comparison
        assert saved_run["duration_seconds"] == 1530  # 25:30 in seconds

    def test_get_runs_retrieves_from_database(
        self, client, mock_dynamodb, auth_headers
    ):
        """Test that GET /runs retrieves runs from the database"""
        # Import app AFTER environment is set
        from src.runs.app import app

        client = TestClient(app)

        # Arrange - First save a run via POST
        run_data = {
            "date": "2024-01-15",
            "distance_km": 3.1,
            "duration": "00:20:00",
            "notes": "Easy pace",
        }
        client.post("/runs", json=run_data, headers=auth_headers)

        # Act - Include authentication headers
        response = client.get("/runs", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        runs = response.json()

        assert len(runs) == 1
        run = runs[0]
        assert run["date"] == "2024-01-15"
        assert run["distance_km"] == 3.1
        assert run["duration"] == "00:20:00"
        assert run["pace"] == "06:27"  # Expected pace per km
        assert run["notes"] == "Easy pace"

    def test_get_runs_empty_database(self, client, mock_dynamodb, auth_headers):
        """Test GET /runs with empty database returns empty list"""
        # Import app AFTER environment is set
        from src.runs.app import app

        client = TestClient(app)

        # Act - Include authentication headers
        response = client.get("/runs", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_post_run_invalid_data_returns_422(
        self, client, mock_dynamodb, auth_headers
    ):
        """Test POST /runs with invalid data returns validation error"""
        # Import app AFTER environment is set
        from src.runs.app import app

        client = TestClient(app)

        # Arrange
        invalid_data = {
            "date": "invalid-date",
            "distance_km": -1,
            "duration": "invalid-duration",
        }

        # Act - Include authentication headers
        response = client.post("/runs", json=invalid_data, headers=auth_headers)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity
