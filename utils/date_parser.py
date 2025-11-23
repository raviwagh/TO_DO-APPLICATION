"""Natural language date parser."""

from datetime import datetime, timedelta
import re


class DateParser:
    """Parse natural language date expressions."""
    
    @staticmethod
    def parse(text: str) -> datetime:
        """Parse natural language date/time expressions.
        
        Supports:
        - today, tomorrow, yesterday
        - next week, next month
        - in X days/weeks/months
        - monday, tuesday, etc.
        - end of week/month
        """
        text = text.lower().strip()
        now = datetime.now()
        
        # Today
        if text == "today":
            return now
        
        # Tomorrow
        if text == "tomorrow":
            return now + timedelta(days=1)
        
        # Yesterday
        if text == "yesterday":
            return now - timedelta(days=1)
        
        # Next week
        if text == "next week":
            return now + timedelta(weeks=1)
        
        # Next month
        if text == "next month":
            return now + timedelta(days=30)
        
        # In X days/weeks/months
        match = re.match(r"in (\d+) (day|week|month)s?", text)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit == "day":
                return now + timedelta(days=amount)
            elif unit == "week":
                return now + timedelta(weeks=amount)
            elif unit == "month":
                return now + timedelta(days=amount * 30)
        
        # Weekday names
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        for day_name, day_num in weekdays.items():
            if day_name in text:
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                if "next" in text:
                    days_ahead += 7
                return now + timedelta(days=days_ahead)
        
        # End of week (Sunday)
        if "end of week" in text:
            days_until_sunday = 6 - now.weekday()
            if days_until_sunday < 0:
                days_until_sunday += 7
            return now + timedelta(days=days_until_sunday)
        
        # End of month
        if "end of month" in text:
            # Get last day of current month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            last_day = next_month - timedelta(days=1)
            return last_day
        
        # If no match, return None
        return None
    
    @staticmethod
    def is_natural_language(text: str) -> bool:
        """Check if text looks like a natural language date."""
        keywords = [
            "today", "tomorrow", "yesterday", "next", "in", 
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "week", "month", "end"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
