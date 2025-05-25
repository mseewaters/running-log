import pytest
from datetime import datetime, date
from decimal import Decimal
import sys
import os


from src.runs.models.run import Run
from src.runs.models.user import User
from src.runs.models.target import Target


class TestUserModel:
    def test_user_creation_with_valid_data(self):
        user = User(
            email="runner@example.com",
            password_hash="hashed_password_123",
            first_name="John",
            last_name="Runner",
        )

        assert user.email == "runner@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.first_name == "John"
        assert user.last_name == "Runner"
        assert user.created_at is not None
        assert user.user_id is not None

    def test_user_email_validation(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                email="invalid-email",
                password_hash="hash123",
                first_name="John",
                last_name="Runner",
            )


class TestRunModel:
    def test_run_creation_with_duration_string(self):
        """Test that we can create a run with hh:mm:ss duration"""
        run = Run(
            user_id="user123",
            date=date(2024, 1, 15),
            distance_km=Decimal("5.2"),
            duration="00:25:30",  # Input as string
            notes="Great morning run",
        )

        # Should store as seconds internally
        assert run.duration_seconds == 1530  # 25*60 + 30 = 1530
        # Should provide formatted output
        assert run.duration_formatted == "00:25:30"

    def test_run_various_duration_formats(self):
        """Test different valid duration formats"""
        test_cases = [
            ("01:30:45", 5445),  # 1 hour 30 min 45 sec
            ("00:05:00", 300),  # 5 minutes
            ("00:00:30", 30),  # 30 seconds
            ("02:00:00", 7200),  # 2 hours
        ]

        for duration_str, expected_seconds in test_cases:
            run = Run(
                user_id="user123",
                date=date(2024, 1, 15),
                distance_km=Decimal("5.0"),
                duration=duration_str,
            )
            assert run.duration_seconds == expected_seconds
            assert run.duration_formatted == duration_str

    def test_invalid_duration_format(self):
        """Test that invalid duration formats raise errors"""
        invalid_durations = [
            "25:30",  # Missing hours
            "1:30:45",  # Single digit hour
            "01:60:00",  # Invalid minutes
            "01:30:60",  # Invalid seconds
            "invalid",  # Not a time format
            "",  # Empty string
        ]

        for invalid_duration in invalid_durations:
            with pytest.raises(ValueError, match="Invalid duration format"):
                Run(
                    user_id="user123",
                    date=date(2024, 1, 15),
                    distance_km=Decimal("5.0"),
                    duration=invalid_duration,
                )

    def test_pace_calculation(self):
        """Test pace calculation in seconds per km"""
        run = Run(
            user_id="user123",
            date=date(2024, 1, 15),
            distance_km=Decimal("5.0"),
            duration="00:25:00",  # 1500 seconds
        )

        # Pace should be 300 seconds per km (5:00 per km)
        assert run.pace_per_km_seconds == 300
        assert run.pace_per_km_formatted == "05:00"

    def test_run_basic_properties(self):
        """Test basic run properties are set correctly"""
        run = Run(
            user_id="user123",
            date=date(2024, 1, 15),
            distance_km=Decimal("5.2"),
            duration="00:25:30",
            notes="Great morning run",
        )

        assert run.user_id == "user123"
        assert run.date == date(2024, 1, 15)
        assert run.distance_km == Decimal("5.2")
        assert run.notes == "Great morning run"
        assert run.run_id is not None
        assert run.created_at is not None


class TestTargetModel:
    def test_monthly_target_creation(self):
        target = Target(
            user_id="user123",
            target_type="monthly",
            period="2024-01",
            distance_km=Decimal("100.0"),
        )

        assert target.user_id == "user123"
        assert target.target_type == "monthly"
        assert target.period == "2024-01"
        assert target.distance_km == Decimal("100.0")
        assert target.target_id is not None

    def test_yearly_target_creation(self):
        target = Target(
            user_id="user123",
            target_type="yearly",
            period="2024",
            distance_km=Decimal("1200.0"),
        )

        assert target.target_type == "yearly"
        assert target.period == "2024"
