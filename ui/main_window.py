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
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # Ctrl+N: New task
        self.bind('<Control-n>', lambda e: self.input_form.clear_form())
        # Ctrl+S: Save/Update task
        self.bind('<Control-s>', lambda e: self._save_shortcut())
        # Delete: Delete selected task
        self.bind('<Delete>', lambda e: self.delete_todo())
        # Ctrl+F: Focus search
        self.bind('<Control-f>', lambda e: self.dashboard.search_entry.focus_set())
        # Escape: Clear form
        self.bind('<Escape>', lambda e: self.clear_form())
        # Ctrl+D: Duplicate task
        self.bind('<Control-d>', lambda e: self.duplicate_task())
        # Ctrl+Shift+C: Clear completed
        self.bind('<Control-Shift-C>', lambda e: self.clear_completed_tasks())
    
    def _save_shortcut(self):
        """Handle Ctrl+S shortcut."""
        if self.input_form.update_button['state'] == 'normal':
            self.update_selected_todo()
        else:
            self.add_new_todo()
    
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
        
        # Input form (left panel) - 65% of space
        self.input_form = InputForm(
            self.paned_window,
            on_add=self.add_new_todo,
            on_update=self.update_selected_todo,
            on_clear=self.clear_form
        )
        self.paned_window.add(self.input_form, weight=65)
        
        # Task list (right panel) - 35% of space
        self.task_list = TaskList(
            self.paned_window,
            on_select=self.on_select_todo,
            on_delete=self.delete_todo,
            on_add_subtask=self.enter_sub_todo_mode,
            theme_config=self.theme_config
        )
        self.task_list.refresh_callback = self.refresh_display
        # Connect context menu callbacks
        self.task_list.duplicate_callback = self.duplicate_task
        self.task_list.toggle_complete_callback = self.toggle_task_completion
        self.paned_window.add(self.task_list, weight=35)
        
        # Start auto-save timer
        self._start_autosave()
        
        # Build menu bar (after all components are created)
        self._build_menu_bar()
    
    def _build_menu_bar(self):
        """Build the menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Task", command=self.input_form.clear_form, accelerator="Ctrl+N")
        file_menu.add_command(label="Save", command=self.save_todos, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Create Backup", command=self._create_backup)
        file_menu.add_command(label="Restore Backup", command=self._restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Duplicate Task", command=self.duplicate_task, accelerator="Ctrl+D")
        edit_menu.add_command(label="Delete Task", command=self.delete_todo, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Completed Tasks", command=self.clear_completed_tasks, accelerator="Ctrl+Shift+C")
        edit_menu.add_command(label="Clear Form", command=self.clear_form, accelerator="Escape")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Focus Search", command=lambda: self.dashboard.search_entry.focus_set(), accelerator="Ctrl+F")
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self.refresh_display)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="About", command=self._show_about)
    
    def on_theme_change(self, theme_name):
        """Handle theme change - applies instantly without restart."""
        self.current_theme = theme_name
        self.theme_config = get_theme_config(theme_name)
        
        # Save theme preference
        self.settings["theme"] = theme_name
        DataManager.save_settings(self.settings)
        
        # Apply theme instantly
        try:
            self.style.theme_use(self.theme_config["base_theme"])
            
            # Update task list colors
            self.task_list.update_theme(self.theme_config)
            
            # Refresh display to apply new colors
            self.refresh_display()
            
            # Show success message
            messagebox.showinfo(
                "Theme Applied",
                f"Theme changed to {self.theme_config['name']}!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {e}")
    
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
    
    def duplicate_task(self):
        """Duplicate the selected task."""
        sel = self.task_list.get_selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a task to duplicate")
            return
        
        if "-" in sel:
            messagebox.showwarning("Warning", "Cannot duplicate sub-tasks")
            return
        
        # Get the task to duplicate
        idx = int(sel)
        original = self.todo_list[idx]
        
        # Create a copy
        import copy
        duplicate = copy.deepcopy(original)
        duplicate["title"] = f"{duplicate['title']} (Copy)"
        duplicate["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duplicate["completed"] = False
        
        # Reset sub-task completion
        for sub in duplicate.get("sub_todos", []):
            sub["completed"] = False
        
        self.todo_list.append(duplicate)
        self.save_todos()
        self.refresh_display()
        messagebox.showinfo("Success", "Task duplicated successfully!")
    
    def clear_completed_tasks(self):
        """Clear all completed tasks."""
        completed_count = sum(1 for t in self.todo_list if t.get("completed"))
        
        if completed_count == 0:
            messagebox.showinfo("Info", "No completed tasks to clear")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {completed_count} completed task(s)?"):
            self.todo_list = [t for t in self.todo_list if not t.get("completed")]
            self.save_todos()
            self.refresh_display()
            self.clear_form()
            messagebox.showinfo("Success", f"Cleared {completed_count} completed task(s)!")
    
    def toggle_task_completion(self):
        """Toggle completion status of selected task."""
        sel = self.task_list.get_selection()
        if not sel:
            return
        
        if "-" in sel:
            # Toggle sub-task
            main_idx, sub_idx = map(int, sel.split("-"))
            parent = self.todo_list[main_idx]
            sub = parent["sub_todos"][sub_idx]
            sub["completed"] = not sub.get("completed", False)
        else:
            # Toggle main task
            idx = int(sel)
            task = self.todo_list[idx]
            task["completed"] = not task.get("completed", False)
        
        self.save_todos()
        self.refresh_display()
    
    def _start_autosave(self):
        """Start auto-save timer (saves every 30 seconds)."""
        def autosave():
            if self.todo_list:
                self.save_todos()
            # Schedule next auto-save
            self.after(30000, autosave)  # 30 seconds
        
        # Start the timer
        self.after(30000, autosave)
    
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
    
    def _create_backup(self):
        """Create a manual backup."""
        from utils.backup_manager import BackupManager
        if BackupManager.create_backup():
            messagebox.showinfo("Success", "Backup created successfully!")
        else:
            messagebox.showerror("Error", "Failed to create backup")
    
    def _restore_backup(self):
        """Restore from a backup."""
        from utils.backup_manager import BackupManager
        
        backups = BackupManager.list_backups()
        if not backups:
            messagebox.showinfo("Info", "No backups available")
            return
        
        # Create a simple dialog to select backup
        dialog = tk.Toplevel(self)
        dialog.title("Restore Backup")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select a backup to restore:", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        for name, timestamp in backups:
            dt = datetime.fromtimestamp(timestamp)
            display = f"{name} - {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            listbox.insert(END, display)
        
        def restore():
            selection = listbox.curselection()
            if selection:
                backup_name = backups[selection[0]][0]
                if BackupManager.restore_backup(backup_name):
                    messagebox.showinfo("Success", "Backup restored! Reloading data...")
                    self.load_todos()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to restore backup")
        
        ttk.Button(dialog, text="Restore", command=restore, bootstyle="success").pack(pady=10)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts = """
Keyboard Shortcuts:

Ctrl+N       New Task
Ctrl+S       Save/Update Task
Ctrl+F       Focus Search
Ctrl+D       Duplicate Task
Ctrl+Shift+C Clear Completed Tasks
Delete       Delete Selected Task
Escape       Clear Form
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
ProTask Manager v2.0

A feature-rich task management application
with modular architecture and theme support.

Features:
• Multiple themes
• Keyboard shortcuts
• Auto-save
• Backup/Restore
• Natural language dates
• And much more!
        """
        messagebox.showinfo("About ProTask Manager", about_text)
