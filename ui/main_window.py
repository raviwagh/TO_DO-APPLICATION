"""Main application window."""

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

from config.settings import APP_NAME, DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE
from config.themes import get_theme_config
from utils.data_manager import DataManager
from ui.components.dashboard import Dashboard
from ui.components.input_form import InputForm
from ui.components.task_list import TaskList
from ui.components.theme_selector import ThemeSelector


class MainWindow(ttk.Window):
    """Main application window."""
    
    def __init__(self, theme_name=None):
        # Load settings
        self.settings = DataManager.load_settings()
        self.current_theme = theme_name or self.settings.get("theme", "superhero")
        self.theme_config = get_theme_config(self.current_theme)
        
        # Initialize window with theme
        super().__init__(themename=self.theme_config["base_theme"])
        
        self.title(APP_NAME)
        self.geometry(DEFAULT_WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        
        # Data
        self.todo_list = []
        self.selected_main_todo_index = None
        self.selected_sub_todo_index = None
        
        # Build UI
        self._build_ui()
        
        # Load data
        self.load_todos()
        
        # Protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _build_ui(self):
        """Build the user interface."""
        # Top frame with theme selector
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=X)
        
        # Theme selector
        self.theme_selector = ThemeSelector(
            top_frame,
            self.current_theme,
            self.on_theme_change
        )
        self.theme_selector.pack(side=LEFT)
        
        # Dashboard
        self.dashboard = Dashboard(
            self,
            on_search_change=self.on_search_change,
            on_export=self.export_to_csv
        )
        self.dashboard.pack(fill=X)
        
        ttk.Separator(self).pack(fill=X, padx=10, pady=5)
        
        # Main split layout
        self.paned_window = ttk.Panedwindow(self, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Input form (left panel)
        self.input_form = InputForm(
            self.paned_window,
            on_add=self.add_new_todo,
            on_update=self.update_selected_todo,
            on_clear=self.clear_form
        )
        self.paned_window.add(self.input_form, weight=1)
        
        # Task list (right panel)
        self.task_list = TaskList(
            self.paned_window,
            on_select=self.on_select_todo,
            on_delete=self.delete_todo,
            on_add_subtask=self.enter_sub_todo_mode,
            theme_config=self.theme_config
        )
        self.task_list.refresh_callback = self.refresh_display
        self.paned_window.add(self.task_list, weight=2)
    
    def on_theme_change(self, theme_name):
        """Handle theme change."""
        self.current_theme = theme_name
        self.theme_config = get_theme_config(theme_name)
        
        # Save theme preference
        self.settings["theme"] = theme_name
        DataManager.save_settings(self.settings)
        
        # Show message
        messagebox.showinfo(
            "Theme Changed",
            f"Theme changed to {self.theme_config['name']}.\nPlease restart the application for full effect."
        )
    
    def on_search_change(self, query):
        """Handle search query change."""
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the task list display."""
        search_query = self.dashboard.get_search_query()
        self.task_list.refresh(self.todo_list, search_query)
        self.dashboard.update_stats(self.todo_list)
    
    def add_new_todo(self):
        """Add a new todo."""
        if self.input_form.editing_sub_todo_mode.get():
            self.save_sub_todo()
            return
        
        data, error = self.input_form.collect_data(is_sub=False)
        if error:
            messagebox.showerror("Validation Error", error)
            return
        
        if data:
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["sub_todos"] = []
            self.todo_list.append(data)
            self.save_todos()
            self.refresh_display()
            self.input_form.clear_form()
    
    def save_sub_todo(self):
        """Save a sub-todo."""
        data, error = self.input_form.collect_data(is_sub=True)
        if error:
            messagebox.showerror("Validation Error", error)
            return
        
        if data and self.selected_main_todo_index is not None:
            parent = self.todo_list[self.selected_main_todo_index]
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parent["sub_todos"].append(data)
            self.save_todos()
            self.refresh_display()
            self.input_form.clear_form()
    
    def update_selected_todo(self):
        """Update the selected todo."""
        if self.selected_main_todo_index is None:
            return
        
        if self.input_form.editing_sub_todo_mode.get() and self.selected_sub_todo_index is not None:
            # Update sub-todo
            data, error = self.input_form.collect_data(is_sub=True)
            if error:
                messagebox.showerror("Validation Error", error)
                return
            
            if data:
                parent = self.todo_list[self.selected_main_todo_index]
                old_sub = parent["sub_todos"][self.selected_sub_todo_index]
                data["created_at"] = old_sub.get("created_at")
                parent["sub_todos"][self.selected_sub_todo_index] = data
                self.save_todos()
                self.refresh_display()
                self.input_form.clear_form()
        else:
            # Update main todo
            data, error = self.input_form.collect_data(is_sub=False)
            if error:
                messagebox.showerror("Validation Error", error)
                return
            
            if data:
                old = self.todo_list[self.selected_main_todo_index]
                data["created_at"] = old.get("created_at")
                data["sub_todos"] = old.get("sub_todos", [])
                
                self.todo_list[self.selected_main_todo_index] = data
                self.save_todos()
                self.refresh_display()
                self.input_form.clear_form()
    
    def delete_todo(self):
        """Delete the selected todo."""
        sel = self.task_list.get_selection()
        if not sel:
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            if "-" in sel:
                main, sub = map(int, sel.split("-"))
                del self.todo_list[main]["sub_todos"][sub]
            else:
                del self.todo_list[int(sel)]
            
            self.save_todos()
            self.refresh_display()
            self.clear_form()
    
    def enter_sub_todo_mode(self):
        """Enter sub-todo creation mode."""
        sel = self.task_list.get_selection()
        if not sel or "-" in sel:
            messagebox.showwarning("Warning", "Select a Main Task first")
            return
        
        self.selected_main_todo_index = int(sel)
        parent_title = self.todo_list[self.selected_main_todo_index]['title']
        
        self.input_form.enter_sub_todo_mode(parent_title)
    
    def on_select_todo(self):
        """Handle todo selection."""
        sel = self.task_list.get_selection()
        if not sel:
            return
        
        if "-" in sel:
            # Subtask selected
            main_idx, sub_idx = map(int, sel.split("-"))
            self.selected_main_todo_index = main_idx
            self.selected_sub_todo_index = sub_idx
            
            todo = self.todo_list[main_idx]["sub_todos"][sub_idx]
            self.input_form.load_todo(todo, is_sub=True)
        else:
            # Main task selected
            self.selected_main_todo_index = int(sel)
            self.selected_sub_todo_index = None
            
            todo = self.todo_list[int(sel)]
            self.input_form.load_todo(todo, is_sub=False)
    
    def clear_form(self):
        """Clear the input form."""
        self.selected_main_todo_index = None
        self.selected_sub_todo_index = None
        self.input_form.clear_form()
    
    def export_to_csv(self):
        """Export todos to CSV."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")]
            )
            if not file_path:
                return
            
            if DataManager.export_to_csv(self.todo_list, file_path):
                messagebox.showinfo("Export Success", f"Exported successfully to {file_path}")
            else:
                messagebox.showerror("Error", "Export failed")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def save_todos(self):
        """Save todos to file."""
        DataManager.save_todos(self.todo_list)
    
    def load_todos(self):
        """Load todos from file."""
        self.todo_list = DataManager.load_todos()
        self.refresh_display()
    
    def on_close(self):
        """Handle window close."""
        if messagebox.askyesno("Exit", "Save and Quit?"):
            self.save_todos()
            self.destroy()
