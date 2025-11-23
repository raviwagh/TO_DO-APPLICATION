"""Input form component for creating and editing tasks."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from config.settings import DATE_FORMAT, DATETIME_FORMAT, PRIORITY_LEVELS, RECURRING_FREQUENCIES
from utils.validators import TimeValidator


class InputForm(ttk.Frame):
    """Task input form with all fields."""
    
    def __init__(self, parent, on_add, on_update, on_clear):
        super().__init__(parent, padding=10)
        self.on_add = on_add
        self.on_update = on_update
        self.on_clear = on_clear
        
        self.editing_sub_todo_mode = tk.BooleanVar(value=False)
        
        # Build form
        self._build_form()
    
    def _build_form(self):
        """Build the input form."""
        # Header
        self.form_header = ttk.Label(
            self,
            text="New Task",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        self.form_header.pack(anchor=W, pady=(0, 10))
        
        # Task Details Group
        self._build_details_group()
        
        # Description Group
        self._build_description_group()
        
        # Advanced Options Group
        self._build_advanced_group()
        
        # Completion Status
        self._build_status_frame()
        
        # Action Buttons
        self._build_action_buttons()
        
        # Initialize toggles
        self.toggle_reminder_options()
        self.toggle_recurring_options()
    
    def _build_details_group(self):
        """Build task details group."""
        details_group = ttk.Labelframe(self, text="Task Details", padding=10)
        details_group.pack(fill=X, pady=5)
        
        # Title
        ttk.Label(details_group, text="Title").pack(anchor=W)
        self.todo_title_entry = ttk.Entry(details_group)
        self.todo_title_entry.pack(fill=X, pady=(0, 5))
        
        # Priority & Due Date Row
        row1 = ttk.Frame(details_group)
        row1.pack(fill=X, pady=5)
        
        ttk.Label(row1, text="Priority").pack(side=LEFT)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(
            row1,
            textvariable=self.priority_var,
            values=PRIORITY_LEVELS,
            state="readonly",
            width=10
        )
        self.priority_combo.pack(side=LEFT, padx=(5, 15))
        
        ttk.Label(row1, text="Due Date").pack(side=LEFT)
        self.due_date_entry = DateEntry(
            row1,
            width=12,
            dateformat='%Y-%m-%d',
            bootstyle="primary"
        )
        self.due_date_entry.pack(side=LEFT, padx=(5, 5))
        
        ttk.Label(row1, text="Time").pack(side=LEFT)
        vcmd = (self.register(self._validate_time), '%P')
        self.due_time_entry = ttk.Entry(row1, width=8, validate='key', validatecommand=vcmd)
        self.due_time_entry.pack(side=LEFT, padx=5)
    
    def _build_description_group(self):
        """Build description group."""
        desc_group = ttk.Labelframe(self, text="Description", padding=10)
        desc_group.pack(fill=BOTH, expand=True, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(desc_group)
        toolbar.pack(fill=X)
        ttk.Button(
            toolbar, text="B", width=3,
            command=self.apply_bold,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=1)
        ttk.Button(
            toolbar, text="I", width=3,
            command=self.apply_italic,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=1)
        ttk.Button(
            toolbar, text="U", width=3,
            command=self.apply_underline,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=1)
        
        self.description_text = ScrolledText(
            desc_group,
            height=5,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.description_text.pack(fill=BOTH, expand=True, pady=5)
        self._setup_text_tags()
    
    def _build_advanced_group(self):
        """Build advanced options group."""
        self.advanced_group = ttk.Labelframe(self, text="Options", padding=10)
        self.advanced_group.pack(fill=X, pady=5)
        
        # Reminder Row
        rem_row = ttk.Frame(self.advanced_group)
        rem_row.pack(fill=X, pady=2)
        
        self.set_reminder_var = tk.BooleanVar()
        self.reminder_check = ttk.Checkbutton(
            rem_row,
            text="Reminder",
            variable=self.set_reminder_var,
            command=self.toggle_reminder_options,
            bootstyle="round-toggle"
        )
        self.reminder_check.pack(side=LEFT)
        
        self.reminder_frame = ttk.Frame(rem_row)
        ttk.Label(self.reminder_frame, text=" @ ").pack(side=LEFT)
        self.reminder_date_entry = DateEntry(
            self.reminder_frame,
            width=11,
            dateformat='%Y-%m-%d',
            bootstyle="info"
        )
        self.reminder_date_entry.pack(side=LEFT)
        
        vcmd = (self.register(self._validate_time), '%P')
        self.reminder_time_entry = ttk.Entry(
            self.reminder_frame,
            width=8,
            validate='key',
            validatecommand=vcmd
        )
        self.reminder_time_entry.pack(side=LEFT, padx=5)
        
        # Recurring Row
        rec_row = ttk.Frame(self.advanced_group)
        rec_row.pack(fill=X, pady=2)
        
        self.set_recurring_var = tk.BooleanVar()
        self.recurring_check = ttk.Checkbutton(
            rec_row,
            text="Recurring",
            variable=self.set_recurring_var,
            command=self.toggle_recurring_options,
            bootstyle="round-toggle"
        )
        self.recurring_check.pack(side=LEFT)
        
        self.recurring_combo = ttk.Combobox(
            rec_row,
            values=RECURRING_FREQUENCIES,
            state="readonly",
            width=10
        )
    
    def _build_status_frame(self):
        """Build completion status frame."""
        self.status_frame = ttk.Frame(self, padding=5)
        self.status_frame.pack(fill=X)
        
        self.completed_var = tk.BooleanVar()
        self.completed_check = ttk.Checkbutton(
            self.status_frame,
            text="Mark Completed",
            variable=self.completed_var,
            bootstyle="success-square-toggle"
        )
        self.completed_check.pack(side=LEFT)
    
    def _build_action_buttons(self):
        """Build action buttons."""
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=X, pady=10)
        
        self.add_button = ttk.Button(
            btn_frame,
            text="Add Task",
            command=self.on_add,
            bootstyle="success"
        )
        self.add_button.pack(side=LEFT, fill=X, expand=True, padx=2)
        
        self.update_button = ttk.Button(
            btn_frame,
            text="Save Changes",
            command=self.on_update,
            state=DISABLED,
            bootstyle="warning"
        )
        self.update_button.pack(side=LEFT, fill=X, expand=True, padx=2)
        
        self.clear_button = ttk.Button(
            btn_frame,
            text="Clear",
            command=self.on_clear,
            bootstyle="secondary"
        )
        self.clear_button.pack(side=LEFT, fill=X, expand=True, padx=2)
    
    def _setup_text_tags(self):
        """Setup text formatting tags."""
        target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
        target.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        target.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        target.tag_configure("underline", underline=1)
    
    def _validate_time(self, P):
        """Validate time input."""
        return TimeValidator.validate_time_format(P)
    
    def apply_bold(self):
        """Apply bold formatting."""
        self._format_text("bold")
    
    def apply_italic(self):
        """Apply italic formatting."""
        self._format_text("italic")
    
    def apply_underline(self):
        """Apply underline formatting."""
        self._format_text("underline")
    
    def _format_text(self, tag):
        """Apply text formatting."""
        try:
            target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
            target.tag_add(tag, "sel.first", "sel.last")
        except tk.TclError:
            pass
    
    def toggle_reminder_options(self):
        """Toggle reminder options visibility."""
        if self.set_reminder_var.get() and not self.editing_sub_todo_mode.get():
            self.reminder_frame.pack(side=LEFT, padx=5)
        else:
            self.reminder_frame.pack_forget()
    
    def toggle_recurring_options(self):
        """Toggle recurring options visibility."""
        if self.set_recurring_var.get() and not self.editing_sub_todo_mode.get():
            self.recurring_combo.pack(side=LEFT, padx=5)
        else:
            self.recurring_combo.pack_forget()
    
    def get_formatted_text(self):
        """Get formatted text from description."""
        target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
        return [{'text': target.get("1.0", "end-1c"), 'formatting': []}]
    
    def collect_data(self, is_sub=False):
        """Collect form data."""
        title = self.todo_title_entry.get().strip()
        if not title:
            return None, "Title is required"
        
        data = {
            "title": title,
            "description_content": self.get_formatted_text(),
            "completed": self.completed_var.get()
        }
        
        if not is_sub:
            data["priority"] = self.priority_var.get()
            
            d_date_str = self.due_date_entry.entry.get()
            if not d_date_str:
                return None, "Due Date is required"
            
            try:
                d_date = datetime.strptime(d_date_str, DATE_FORMAT).date()
            except ValueError:
                return None, "Invalid Date Format"
            
            d_time = self.due_time_entry.get().strip() or "23:59"
            try:
                data["due_datetime"] = datetime.combine(
                    d_date,
                    datetime.strptime(d_time, "%H:%M").time()
                ).strftime(DATETIME_FORMAT)
            except:
                return None, "Invalid Time Format (HH:MM)"
            
            data["has_reminder"] = self.set_reminder_var.get()
            if data["has_reminder"]:
                r_date_str = self.reminder_date_entry.entry.get()
                r_time = self.reminder_time_entry.get().strip()
                if not r_time or not r_date_str:
                    return None, "Reminder date and time required"
                try:
                    r_date = datetime.strptime(r_date_str, DATE_FORMAT).date()
                    data["reminder_datetime"] = datetime.combine(
                        r_date,
                        datetime.strptime(r_time, "%H:%M").time()
                    ).strftime(DATETIME_FORMAT)
                except:
                    return None, "Invalid reminder date/time"
            else:
                data["reminder_datetime"] = None
            
            data["is_recurring"] = self.set_recurring_var.get()
            data["recurring_frequency"] = self.recurring_combo.get() if data["is_recurring"] else "None"
        
        return data, None
    
    def clear_form(self, soft=False):
        """Clear the form."""
        self.editing_sub_todo_mode.set(False)
        
        self.form_header.config(text="New Task", bootstyle="primary")
        self.todo_title_entry.delete(0, END)
        
        target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
        target.delete("1.0", END)
        
        self.due_time_entry.delete(0, END)
        
        self.priority_combo.config(state="readonly")
        
        self.due_date_entry.entry.config(state="normal")
        self.due_date_entry.button.config(state="normal")
        self.due_date_entry.entry.delete(0, END)
        self.due_date_entry.entry.insert(0, datetime.now().strftime(DATE_FORMAT))
        
        self.due_time_entry.config(state="normal")
        self.advanced_group.pack(fill=X, pady=5)
        self.toggle_reminder_options()
        
        self.add_button.config(text="Add Task", bootstyle="success", state=NORMAL)
        self.update_button.config(state=DISABLED)
    
    def load_todo(self, todo, is_sub=False):
        """Load todo data into form."""
        self.clear_form(soft=True)
        
        self.todo_title_entry.insert(0, todo["title"])
        self.completed_var.set(todo.get("completed", False))
        
        desc = todo.get("description_content", [])
        if desc and isinstance(desc, list):
            target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
            for line in desc:
                target.insert(END, line.get('text', '') + "\n")
        
        if not is_sub:
            self.form_header.config(text="Edit Task", bootstyle="warning")
            
            self.priority_var.set(todo.get("priority", "Medium"))
            
            if todo.get("due_datetime"):
                try:
                    dt = datetime.strptime(todo["due_datetime"], DATETIME_FORMAT)
                    self.due_date_entry.entry.delete(0, END)
                    self.due_date_entry.entry.insert(0, dt.strftime(DATE_FORMAT))
                    self.due_time_entry.insert(0, dt.strftime("%H:%M"))
                except:
                    pass
            
            self.set_reminder_var.set(todo.get("has_reminder", False))
            if todo.get("has_reminder") and todo.get("reminder_datetime"):
                try:
                    rdt = datetime.strptime(todo["reminder_datetime"], DATETIME_FORMAT)
                    self.reminder_date_entry.entry.delete(0, END)
                    self.reminder_date_entry.entry.insert(0, rdt.strftime(DATE_FORMAT))
                    self.reminder_time_entry.insert(0, rdt.strftime("%H:%M"))
                except:
                    pass
            self.toggle_reminder_options()
            
            self.set_recurring_var.set(todo.get("is_recurring", False))
            if todo.get("is_recurring"):
                self.recurring_combo.set(todo.get("recurring_frequency"))
            self.toggle_recurring_options()
        else:
            self.form_header.config(text="Edit Sub-Task", bootstyle="warning")
            self.editing_sub_todo_mode.set(True)
            self.advanced_group.pack_forget()
            self.due_date_entry.entry.config(state=DISABLED)
            self.due_date_entry.button.config(state=DISABLED)
            self.priority_combo.config(state=DISABLED)
            self.due_time_entry.config(state=DISABLED)
        
        self.add_button.config(state=DISABLED)
        self.update_button.config(state=NORMAL)
    
    def enter_sub_todo_mode(self, parent_title):
        """Enter sub-todo creation mode."""
        self.clear_form(soft=True)
        self.editing_sub_todo_mode.set(True)
        self.form_header.config(text=f"Adding Sub-Task to: {parent_title}", bootstyle="info")
        
        self.priority_combo.config(state=DISABLED)
        self.due_date_entry.entry.config(state=DISABLED)
        self.due_date_entry.button.config(state=DISABLED)
        self.due_time_entry.config(state=DISABLED)
        self.advanced_group.pack_forget()
        
        self.add_button.config(text="Add Sub-Task", bootstyle="info")
