import uuid
from datetime import datetime, date
from decimal import Decimal
import re


class Run:
    def __init__(
        self,
        user_id: str,
        date: date,
        distance_km: Decimal,
        duration: str,
        notes: str = "",
    ):
        self.user_id = user_id
        self.date = date
        self.distance_km = distance_km
        self.notes = notes
        self.run_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()

        # Parse and store duration
        self.duration_seconds = self._parse_duration(duration)

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string (HH:MM:SS) into total seconds"""
        if not duration_str:
            raise ValueError("Invalid duration format: empty string")

        # Regex pattern for HH:MM:SS format
        pattern = r"^(\d{2}):(\d{2}):(\d{2})$"
        match = re.match(pattern, duration_str)

        if not match:
            raise ValueError("Invalid duration format: must be HH:MM:SS")

        hours, minutes, seconds = map(int, match.groups())

        # Validate ranges
        if minutes >= 60:
            raise ValueError("Invalid duration format: minutes must be < 60")
        if seconds >= 60:
            raise ValueError("Invalid duration format: seconds must be < 60")

        return hours * 3600 + minutes * 60 + seconds

    @property
    def duration_formatted(self) -> str:
        """Format duration seconds back to HH:MM:SS string"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def pace_per_km_seconds(self) -> int:
        """Calculate pace in seconds per kilometer"""
        if self.distance_km == 0:
            return 0
        return int(self.duration_seconds / float(self.distance_km))

    @property
    def pace_per_km_formatted(self) -> str:
        """Format pace as MM:SS per kilometer"""
        pace_seconds = self.pace_per_km_seconds
        minutes = pace_seconds // 60
        seconds = pace_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
