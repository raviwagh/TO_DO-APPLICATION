"""ProTask Manager - Modular Todo Application with Theme Support.

A feature-rich task management application with:
- Modular architecture for better maintainability
- Multiple theme support (6 themes: 3 light, 3 dark)
- Task and sub-task management
- Priority levels and due dates
- Filtering and sorting
- Search functionality
- CSV export
"""

from ui.main_window import MainWindow
from utils.data_manager import DataManager


def main():
    """Main entry point for the application."""
    # Load saved theme preference
    settings = DataManager.load_settings()
    theme = settings.get("theme", "superhero")
    
    # Create and run application
    app = MainWindow(theme_name=theme)
    app.place_window_center()
    app.mainloop()


if __name__ == "__main__":
    main()
