"""Application settings and constants."""

import os
from pathlib import Path

# Application Info
APP_NAME = "ProTask Manager"
APP_VERSION = "2.0.0"

# File Paths
BASE_DIR = Path(__file__).parent.parent
TODO_FILE = BASE_DIR / "todos.json"
SETTINGS_FILE = BASE_DIR / "settings.json"

# Date/Time Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_DATE_FORMAT = "%Y-%m-%d %H:%M"

# UI Settings
DEFAULT_WINDOW_SIZE = "1280x800"
MIN_WINDOW_SIZE = (1000, 700)

# Default Theme
DEFAULT_THEME = "superhero"

# Priority Levels
PRIORITY_LEVELS = ["High", "Medium", "Low"]

# Recurring Frequencies
RECURRING_FREQUENCIES = ["Daily", "Weekly", "Monthly"]

# Filter Options
FILTER_OPTIONS = ["All", "Active", "Completed", "Overdue"]

# Sort Options
SORT_OPTIONS = ["Priority", "Due Date", "Created"]
