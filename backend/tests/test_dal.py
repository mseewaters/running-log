import pytest
import boto3
import os
import sys
from moto import mock_aws
from datetime import date
from decimal import Decimal

# Import our models
from src.runs.models.user import User
from src.runs.models.run import Run
from src.runs.models.target import Target

# Import DAL functions (we'll create these next)
from src.runs.dal.user_dal import save_user, get_user_by_id, get_user_by_email
from src.runs.dal.run_dal import save_run, get_runs_by_user, get_run_by_id
from src.runs.dal.target_dal import save_target, get_targets_by_user


@pytest.fixture
def dynamodb_tables():
    """Set up mock DynamoDB tables for testing"""
    # FIX: Set environment variables BEFORE importing DAL functions
    os.environ["USERS_TABLE"] = "test-users"
    os.environ["RUNS_TABLE"] = "test-runs"
    os.environ["TARGETS_TABLE"] = "test-targets"

    # FORCE MODULE RELOAD to pick up new environment variables
    dal_modules = [
        "src.runs.dal.user_dal",
        "src.runs.dal.run_dal",
        "src.runs.dal.target_dal",
    ]
    for module in dal_modules:
        if module in sys.modules:
            del sys.modules[module]

    with mock_aws():
        # Create mock DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create Users table
        users_table = dynamodb.create_table(
            TableName="test-users",
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

        # Create Runs table
        runs_table = dynamodb.create_table(
            TableName="test-runs",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "run_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "run_id", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user-date-index",
                    "KeySchema": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "date", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Create Targets table
        targets_table = dynamodb.create_table(
            TableName="test-targets",
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

        yield {"users": users_table, "runs": runs_table, "targets": targets_table}


class TestUserDAL:
    def test_save_and_get_user(self, dynamodb_tables):
        """Test saving a user and retrieving by ID"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )

        # Save user
        save_user(user)

        # Retrieve user
        retrieved_user = get_user_by_id(user.user_id)

        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.first_name == "John"
        assert retrieved_user.last_name == "Doe"
        assert retrieved_user.user_id == user.user_id

    def test_get_user_by_email(self, dynamodb_tables):
        """Test retrieving user by email"""
        user = User(
            email="findme@example.com",
            password_hash="hashed_password",
            first_name="Jane",
            last_name="Smith",
        )

        save_user(user)

        retrieved_user = get_user_by_email("findme@example.com")
        assert retrieved_user is not None
        assert retrieved_user.user_id == user.user_id


class TestRunDAL:
    def test_save_and_get_run(self, dynamodb_tables):
        """Test saving a run and retrieving by ID"""
        run = Run(
            user_id="user123",
            date=date(2024, 1, 15),
            distance_km=Decimal("5.2"),
            duration="00:25:30",
            notes="Morning run",
        )

        save_run(run)

        retrieved_run = get_run_by_id("user123", run.run_id)
        assert retrieved_run is not None
        assert retrieved_run.distance_km == Decimal("5.2")
        assert retrieved_run.duration_seconds == 1530

    def test_get_runs_by_user(self, dynamodb_tables):
        """Test retrieving all runs for a user"""
        user_id = "user123"

        run1 = Run(
            user_id=user_id,
            date=date(2024, 1, 15),
            distance_km=Decimal("5.0"),
            duration="00:25:00",
        )
        run2 = Run(
            user_id=user_id,
            date=date(2024, 1, 16),
            distance_km=Decimal("3.0"),
            duration="00:18:00",
        )

        save_run(run1)
        save_run(run2)

        runs = get_runs_by_user(user_id)
        assert len(runs) == 2


class TestTargetDAL:
    def test_save_and_get_target(self, dynamodb_tables):
        """Test saving and retrieving targets"""
        target = Target(
            user_id="user123",
            target_type="monthly",
            period="2024-01",
            distance_km=Decimal("100.0"),
        )

        save_target(target)

        targets = get_targets_by_user("user123")
        assert len(targets) == 1
        assert targets[0].distance_km == Decimal("100.0")
