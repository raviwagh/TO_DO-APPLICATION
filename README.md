# ProTask Manager - Modular Todo Application v2.0

A feature-rich, modular task management application built with Python and ttkbootstrap.

## ✨ What's New in v2.0

**UI/UX Enhancements:**
- 🎹 Keyboard shortcuts (Ctrl+N, Ctrl+S, Ctrl+D, Delete, Escape, Ctrl+F, Ctrl+Shift+C)
- ⚡ Instant theme switching (no restart required!)
- 🔴🟡🟢 Priority icons for visual clarity
- █████░░░░░ Visual progress bars for sub-tasks
- 📊 Enhanced dashboard with emoji stats
- 🖱️ Right-click context menu for quick actions

**Smart Features:**
- 📅 Natural language date parsing ("tomorrow", "next week", "in 3 days")
- 💾 Auto-save every 30 seconds
- 🔄 Backup & restore system with automatic rotation
- 📋 Task duplication
- 🗑️ Bulk clear completed tasks
- ✅ Quick toggle task completion

**Professional Polish:**
- 📑 Full menu bar (File, Edit, View, Help)
- ⌨️ Keyboard shortcuts reference
- ℹ️ About dialog
- 🎨 6 beautiful themes (3 light, 3 dark)
  - **Superhero** (Dark with blue accents)
  - **Cosmo** (Clean light theme)
  - **Darkly** (Sleek dark theme)
  - **Flatly** (Flat design light)
  - **Cyborg** (Futuristic dark with cyan)
  - **Solar** (Warm solarized light)

🔍 **Advanced Features**
- Real-time search across tasks
- Filter by status (All, Active, Completed, Overdue)
- Sort by Priority, Due Date, or Created date
- Progress tracking for tasks with sub-tasks
- Reminder settings
- Recurring tasks
- Export to CSV

📊 **Dashboard**
- Live statistics (Total, Active, Overdue tasks)
- Quick search functionality
- One-click CSV export

## Project Structure

```
TO_DO APPLICATION/
├── main.py                 # Application entry point
├── config/                 # Configuration module
│   ├── settings.py         # App constants and settings
│   └── themes.py           # Theme configurations
├── models/                 # Data models
│   └── todo.py             # Todo and SubTodo classes
├── ui/                     # User interface
│   ├── main_window.py      # Main application window
│   └── components/         # UI components
│       ├── dashboard.py    # Stats and search
│       ├── input_form.py   # Task input form
│       ├── task_list.py    # Task treeview
│       └── theme_selector.py  # Theme switcher
├── utils/                  # Utilities
│   ├── data_manager.py     # Data persistence
│   └── validators.py       # Input validation
└── todos.json              # Data storage
```

## Installation

### Requirements
- Python 3.7+
- ttkbootstrap

### Setup

1. Install dependencies:
```bash
pip install ttkbootstrap
```

2. Run the application:
```bash
python main.py
```

## Usage

### Creating Tasks
1. Fill in the task details in the left panel
2. Set priority, due date, and time
3. Add a description (supports basic formatting)
4. Optionally set reminders and recurring options
5. Click "Add Task"

### Managing Tasks
- **Edit**: Click on a task in the list to load it into the form
- **Delete**: Select a task and click the "🗑️ Delete" button
- **Complete**: Edit a task and check "Mark Completed"

### Sub-Tasks
1. Select a main task
2. Click "➕ Sub-Task"
3. Enter sub-task details
4. Click "Add Sub-Task"

### Filtering and Sorting
1. Use the Filter dropdown to show specific task types
2. Use the Sort dropdown to organize tasks
3. Click "Apply" to refresh the view

### Search
Type in the search box to filter tasks by title or description in real-time.

### Changing Themes
1. Click the theme dropdown in the top-left
2. Select your preferred theme
3. Click "Apply Theme"
4. Restart the application for full effect

### Exporting Data
Click "Export CSV" to save your tasks to a CSV file.

## Architecture Benefits

### Modular Design
- **Separation of Concerns**: Each module has a specific responsibility
- **Maintainability**: Easy to update and fix individual components
- **Scalability**: Simple to add new features
- **Testability**: Components can be tested independently

### Configuration Management
- Centralized settings and constants
- Easy theme customization
- Persistent user preferences

### Data Layer
- Clean data models with business logic
- Separate data persistence layer
- Easy to switch storage backends

### UI Components
- Reusable components
- Clear component boundaries
- Event-driven architecture

## Customization

### Adding New Themes
Edit `config/themes.py` and add a new theme configuration:

```python
"mytheme": {
    "name": "My Theme",
    "type": "dark",  # or "light"
    "base_theme": "darkly",
    "colors": {
        "high_priority": "#ff0000",
        "medium_priority": "#ffaa00",
        "low_priority": "#00ff00",
        # ... more colors
    },
    "description": "My custom theme"
}
```

### Modifying Settings
Edit `config/settings.py` to change default values, file paths, or add new constants.

## Data Storage

Tasks are stored in `todos.json` in JSON format. User preferences (like theme selection) are stored in `settings.json`.

## License

This is a personal project for task management.

## Credits

Built with:
- Python
- ttkbootstrap (Bootstrap-themed Tkinter)
- Standard library modules (json, csv, datetime, etc.)
