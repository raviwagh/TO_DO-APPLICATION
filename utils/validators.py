"""Input validation utilities."""

import re
from datetime import datetime
from config.settings import DATE_FORMAT, DATETIME_FORMAT


class TimeValidator:
    """Validates time input."""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Validate time string in HH:MM format."""
        if time_str == "":
            return True
        if re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", time_str):
            return True
        if re.match(r"^\d{0,2}:?\d{0,2}$", time_str):
            return True
        return False
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate date string."""
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_datetime_format(datetime_str: str) -> bool:
        """Validate datetime string."""
        try:
            datetime.strptime(datetime_str, DATETIME_FORMAT)
            return True
        except ValueError:
            return False
