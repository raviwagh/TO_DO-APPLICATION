"""Todo data models."""

from datetime import datetime
from typing import List, Dict, Optional
from config.settings import DATETIME_FORMAT


class SubTodoItem:
    """Represents a sub-task."""
    
    def __init__(self, title: str, description_content: List[Dict] = None, 
                 completed: bool = False, created_at: str = None):
        self.title = title
        self.description_content = description_content or []
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "description_content": self.description_content,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SubTodoItem':
        """Create instance from dictionary."""
        return cls(
            title=data.get("title", ""),
            description_content=data.get("description_content", []),
            completed=data.get("completed", False),
            created_at=data.get("created_at")
        )


class TodoItem:
    """Represents a main task."""
    
    def __init__(self, title: str, priority: str = "Medium", 
                 due_datetime: str = None, description_content: List[Dict] = None,
                 completed: bool = False, has_reminder: bool = False,
                 reminder_datetime: str = None, is_recurring: bool = False,
                 recurring_frequency: str = "None", created_at: str = None,
                 sub_todos: List[SubTodoItem] = None):
        self.title = title
        self.priority = priority
        self.due_datetime = due_datetime
        self.description_content = description_content or []
        self.completed = completed
        self.has_reminder = has_reminder
        self.reminder_datetime = reminder_datetime
        self.is_recurring = is_recurring
        self.recurring_frequency = recurring_frequency
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sub_todos = sub_todos or []
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_datetime or self.completed:
            return False
        try:
            due_dt = datetime.strptime(self.due_datetime, DATETIME_FORMAT)
            return due_dt < datetime.now()
        except:
            return False
    
    def get_progress(self) -> int:
        """Calculate progress percentage based on sub-tasks."""
        if not self.sub_todos:
            return 0
        completed_count = sum(1 for sub in self.sub_todos if sub.completed)
        return int((completed_count / len(self.sub_todos)) * 100)
    
    def get_status(self) -> str:
        """Get current status of the task."""
        if self.completed:
            return "Done"
        if self.is_overdue():
            return "Overdue"
        return "Active"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "priority": self.priority,
            "due_datetime": self.due_datetime,
            "description_content": self.description_content,
            "completed": self.completed,
            "has_reminder": self.has_reminder,
            "reminder_datetime": self.reminder_datetime,
            "is_recurring": self.is_recurring,
            "recurring_frequency": self.recurring_frequency,
            "created_at": self.created_at,
            "sub_todos": [sub.to_dict() if isinstance(sub, SubTodoItem) else sub 
                         for sub in self.sub_todos]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        """Create instance from dictionary."""
        sub_todos_data = data.get("sub_todos", [])
        sub_todos = [SubTodoItem.from_dict(sub) if isinstance(sub, dict) else sub 
                     for sub in sub_todos_data]
        
        return cls(
            title=data.get("title", ""),
            priority=data.get("priority", "Medium"),
            due_datetime=data.get("due_datetime"),
            description_content=data.get("description_content", []),
            completed=data.get("completed", False),
            has_reminder=data.get("has_reminder", False),
            reminder_datetime=data.get("reminder_datetime"),
            is_recurring=data.get("is_recurring", False),
            recurring_frequency=data.get("recurring_frequency", "None"),
            created_at=data.get("created_at"),
            sub_todos=sub_todos
        )
