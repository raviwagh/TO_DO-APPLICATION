"""Data management utilities."""

import json
import csv
from pathlib import Path
from typing import List, Dict
from models.todo import TodoItem
from config.settings import TODO_FILE, SETTINGS_FILE, DEFAULT_THEME


class DataManager:
    """Manages data persistence for todos and settings."""
    
    @staticmethod
    def load_todos() -> List[Dict]:
        """Load todos from JSON file."""
        try:
            if Path(TODO_FILE).exists():
                with open(TODO_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading todos: {e}")
            return []
    
    @staticmethod
    def save_todos(todos: List[Dict]) -> bool:
        """Save todos to JSON file."""
        try:
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump(todos, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving todos: {e}")
            return False
    
    @staticmethod
    def export_to_csv(todos: List[Dict], file_path: str) -> bool:
        """Export todos to CSV file."""
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Title", "Priority", "Due Date", "Status", "Description"])
                
                for todo in todos:
                    desc = " ".join([l.get('text', '') for l in todo.get("description_content", [])])
                    status = "Done" if todo.get('completed') else "Active"
                    writer.writerow([
                        "Main", 
                        todo['title'], 
                        todo.get('priority', ''), 
                        todo.get('due_datetime', ''), 
                        status, 
                        desc
                    ])
                    
                    for sub in todo.get("sub_todos", []):
                        sub_desc = " ".join([l.get('text', '') for l in sub.get("description_content", [])])
                        sub_status = "Done" if sub.get('completed') else "Active"
                        writer.writerow([
                            "Sub", 
                            sub['title'], 
                            "-", 
                            "-", 
                            sub_status, 
                            sub_desc
                        ])
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def load_settings() -> Dict:
        """Load application settings."""
        try:
            if Path(SETTINGS_FILE).exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"theme": DEFAULT_THEME}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {"theme": DEFAULT_THEME}
    
    @staticmethod
    def save_settings(settings: Dict) -> bool:
        """Save application settings."""
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
