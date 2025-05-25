import uuid
from datetime import datetime
from decimal import Decimal
import re


class Target:
    def __init__(
        self, user_id: str, target_type: str, period: str, distance_km: Decimal
    ):
        # Validate target type
        self._validate_target_type(target_type)

        # Validate period format
        self._validate_period(target_type, period)

        self.user_id = user_id
        self.target_type = target_type
        self.period = period
        self.distance_km = distance_km
        self.target_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()

    def _validate_target_type(self, target_type: str) -> None:
        """Validate target type is either 'monthly' or 'yearly'"""
        valid_types = ["monthly", "yearly"]
        if target_type not in valid_types:
            raise ValueError(f"Invalid target type: must be one of {valid_types}")

    def _validate_period(self, target_type: str, period: str) -> None:
        """Validate period format based on target type"""
        if target_type == "monthly":
            # Format should be YYYY-MM
            pattern = r"^\d{4}-\d{2}$"
            if not re.match(pattern, period):
                raise ValueError("Invalid monthly period format: must be YYYY-MM")

            # Validate month is 01-12
            year, month = period.split("-")
            if not (1 <= int(month) <= 12):
                raise ValueError("Invalid month: must be 01-12")

        elif target_type == "yearly":
            # Format should be YYYY
            pattern = r"^\d{4}$"
            if not re.match(pattern, period):
                raise ValueError("Invalid yearly period format: must be YYYY")

    @property
    def period_display(self) -> str:
        """Return human-readable period format"""
        if self.target_type == "monthly":
            year, month = self.period.split("-")
            month_names = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            return f"{month_names[int(month) - 1]} {year}"
        else:  # yearly
            return self.period

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"Target(target_id='{self.target_id}', type='{self.target_type}', period='{self.period}', distance={self.distance_km}km)"
