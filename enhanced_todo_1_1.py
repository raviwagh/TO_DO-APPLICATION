import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
from ttkbootstrap.widgets import DateEntry 
from datetime import datetime, timedelta
import json
import re
import csv

# --- Constants ---
TODO_FILE = "todos.json"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

class TodoListApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero") 
        self.title("ProTask Manager")
        self.geometry("1280x800")
        self.minsize(1000, 700)

        # Data Storage
        self.todo_list = []
        self.selected_main_todo_index = None 
        self.selected_sub_todo_index = None 
        self.current_filter = "All"
        self.current_sort = "Due Date"
        self.search_query = ""
        self.editing_sub_todo_mode = tk.BooleanVar(value=False)

        # UI Layout
        self._build_ui()
        self.load_todos()
        
        # Protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Helper Methods (Moved Up for Safety) ---
    def apply_bold(self): 
        self._format_text("bold")

    def apply_italic(self): 
        self._format_text("italic")

    def apply_underline(self): 
        self._format_text("underline")

    def _format_text(self, tag):
        try:
            # Check if text widget is accessible directly or via .text attribute
            if hasattr(self.description_text, 'text'):
                self.description_text.text.tag_add(tag, "sel.first", "sel.last")
            else:
                self.description_text.tag_add(tag, "sel.first", "sel.last")
        except tk.TclError:
            pass # No selection made

    def _build_ui(self):
        """Constructs the modern Grid/Frame layout."""
        
        # 1. Top Dashboard (Stats & Search)
        dash_frame = ttk.Frame(self, padding=10)
        dash_frame.pack(fill=X)
        
        self.stats_label = ttk.Label(dash_frame, text="Total: 0 | Active: 0 | Overdue: 0", 
                                     font=("Helvetica", 12, "bold"), bootstyle="info")
        self.stats_label.pack(side=LEFT, padx=10)

        # Search Bar
        search_frame = ttk.Frame(dash_frame)
        search_frame.pack(side=RIGHT)
        ttk.Label(search_frame, text="🔍").pack(side=LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=LEFT)
        
        ttk.Button(dash_frame, text="Export CSV", command=self.export_to_csv, bootstyle="outline-secondary").pack(side=RIGHT, padx=20)
        
        ttk.Separator(self).pack(fill=X, padx=10, pady=5)

        # 2. Main Split Layout
        self.paned_window = ttk.Panedwindow(self, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- LEFT PANEL: INPUT FORM ---
        self.input_frame = ttk.Frame(self.paned_window, padding=10)
        self.paned_window.add(self.input_frame, weight=1) 

        # Header for Input
        self.form_header = ttk.Label(self.input_frame, text="New Task", font=("Helvetica", 16, "bold"), bootstyle="primary")
        self.form_header.pack(anchor=W, pady=(0, 10))

        # Input Group: Core Details
        details_group = ttk.Labelframe(self.input_frame, text="Task Details", padding=10)
        details_group.pack(fill=X, pady=5)

        ttk.Label(details_group, text="Title").pack(anchor=W)
        self.todo_title_entry = ttk.Entry(details_group)
        self.todo_title_entry.pack(fill=X, pady=(0, 5))

        # Priority & Due Date Row
        row1 = ttk.Frame(details_group)
        row1.pack(fill=X, pady=5)
        
        ttk.Label(row1, text="Priority").pack(side=LEFT)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(row1, textvariable=self.priority_var, 
                                           values=["High", "Medium", "Low"], state="readonly", width=10)
        self.priority_combo.pack(side=LEFT, padx=(5, 15))

        ttk.Label(row1, text="Due Date").pack(side=LEFT)
        self.due_date_entry = DateEntry(row1, width=12, dateformat='%Y-%m-%d', bootstyle="primary")
        self.due_date_entry.pack(side=LEFT, padx=(5, 5))

        ttk.Label(row1, text="Time").pack(side=LEFT)
        vcmd = (self.register(self.validate_time), '%P')
        self.due_time_entry = ttk.Entry(row1, width=8, validate='key', validatecommand=vcmd)
        self.due_time_entry.pack(side=LEFT, padx=5)

        # Input Group: Description
        desc_group = ttk.Labelframe(self.input_frame, text="Description", padding=10)
        desc_group.pack(fill=BOTH, expand=True, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(desc_group)
        toolbar.pack(fill=X)
        ttk.Button(toolbar, text="B", width=3, command=self.apply_bold, bootstyle="secondary-outline").pack(side=LEFT, padx=1)
        ttk.Button(toolbar, text="I", width=3, command=self.apply_italic, bootstyle="secondary-outline").pack(side=LEFT, padx=1)
        ttk.Button(toolbar, text="U", width=3, command=self.apply_underline, bootstyle="secondary-outline").pack(side=LEFT, padx=1)

        self.description_text = ScrolledText(desc_group, height=5, wrap=tk.WORD, font=("Segoe UI", 10))
        self.description_text.pack(fill=BOTH, expand=True, pady=5)
        self._setup_text_tags()

        # Input Group: Advanced (Reminders/Recurring)
        self.advanced_group = ttk.Labelframe(self.input_frame, text="Options", padding=10)
        self.advanced_group.pack(fill=X, pady=5)

        # Reminder Row
        rem_row = ttk.Frame(self.advanced_group)
        rem_row.pack(fill=X, pady=2)
        self.set_reminder_var = tk.BooleanVar()
        self.reminder_check = ttk.Checkbutton(rem_row, text="Reminder", variable=self.set_reminder_var, command=self.toggle_reminder_options, bootstyle="round-toggle")
        self.reminder_check.pack(side=LEFT)
        
        self.reminder_frame = ttk.Frame(rem_row) # Dynamic container
        ttk.Label(self.reminder_frame, text=" @ ").pack(side=LEFT)
        self.reminder_date_entry = DateEntry(self.reminder_frame, width=11, dateformat='%Y-%m-%d', bootstyle="info")
        self.reminder_date_entry.pack(side=LEFT)
        self.reminder_time_entry = ttk.Entry(self.reminder_frame, width=8, validate='key', validatecommand=vcmd)
        self.reminder_time_entry.pack(side=LEFT, padx=5)

        # Recurring Row
        rec_row = ttk.Frame(self.advanced_group)
        rec_row.pack(fill=X, pady=2)
        self.set_recurring_var = tk.BooleanVar()
        self.recurring_check = ttk.Checkbutton(rec_row, text="Recurring", variable=self.set_recurring_var, command=self.toggle_recurring_options, bootstyle="round-toggle")
        self.recurring_check.pack(side=LEFT)

        self.recurring_combo = ttk.Combobox(rec_row, values=["Daily", "Weekly", "Monthly"], state="readonly", width=10)

        # Completion Status (Hidden for new, visible for edit)
        self.status_frame = ttk.Frame(self.input_frame, padding=5)
        self.status_frame.pack(fill=X)
        self.completed_var = tk.BooleanVar()
        self.completed_check = ttk.Checkbutton(self.status_frame, text="Mark Completed", variable=self.completed_var, bootstyle="success-square-toggle")
        self.completed_check.pack(side=LEFT)

        # Action Buttons
        btn_frame = ttk.Frame(self.input_frame, padding=10)
        btn_frame.pack(fill=X, pady=10)
        
        self.add_button = ttk.Button(btn_frame, text="Add Task", command=self.add_new_todo, bootstyle="success")
        self.add_button.pack(side=LEFT, fill=X, expand=True, padx=2)
        
        self.update_button = ttk.Button(btn_frame, text="Save Changes", command=self.update_selected_todo, state=DISABLED, bootstyle="warning")
        self.update_button.pack(side=LEFT, fill=X, expand=True, padx=2)

        self.clear_button = ttk.Button(btn_frame, text="Clear", command=lambda: self.clear_form(), bootstyle="secondary")
        self.clear_button.pack(side=LEFT, fill=X, expand=True, padx=2)

        # --- RIGHT PANEL: LIST VIEW ---
        self.list_frame = ttk.Frame(self.paned_window, padding=10)
        self.paned_window.add(self.list_frame, weight=2)

        # Filter Controls
        filter_frame = ttk.Frame(self.list_frame)
        filter_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=LEFT)
        self.filter_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["All", "Active", "Completed", "Overdue"], 
                     state="readonly", width=10).pack(side=LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Sort:").pack(side=LEFT, padx=(15,0))
        self.sort_var = tk.StringVar(value="Due Date")
        ttk.Combobox(filter_frame, textvariable=self.sort_var, values=["Priority", "Due Date", "Created"], 
                     state="readonly", width=12).pack(side=LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Apply", command=self.apply_filters_and_sort, bootstyle="outline-primary").pack(side=LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🗑️ Delete", command=self.delete_todo, bootstyle="danger-outline").pack(side=RIGHT)
        ttk.Button(filter_frame, text="➕ Sub-Task", command=self.enter_sub_todo_mode, bootstyle="info-outline").pack(side=RIGHT, padx=5)

        # Treeview
        cols = ("Priority", "Due Date", "Progress", "Status")
        self.todo_tree = ttk.Treeview(self.list_frame, columns=cols, show='tree headings', selectmode='browse', bootstyle="primary")
        
        self.todo_tree.heading("#0", text="Task Title")
        self.todo_tree.heading("Priority", text="Priority")
        self.todo_tree.heading("Due Date", text="Due Date")
        self.todo_tree.heading("Progress", text="Progress")
        self.todo_tree.heading("Status", text="Status")

        self.todo_tree.column("#0", width=300)
        self.todo_tree.column("Priority", width=80, anchor=CENTER)
        self.todo_tree.column("Due Date", width=120, anchor=CENTER)
        self.todo_tree.column("Progress", width=80, anchor=CENTER)
        self.todo_tree.column("Status", width=80, anchor=CENTER)

        # Scrollbar
        vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=vsb.set)
        self.todo_tree.bind('<<TreeviewSelect>>', self.on_select_todo)
        
        vsb.pack(side=RIGHT, fill=Y)
        self.todo_tree.pack(side=LEFT, fill=BOTH, expand=True)

        self._configure_tags()
        
        # Initialize Toggles
        self.toggle_reminder_options()
        self.toggle_recurring_options()

    def _setup_text_tags(self):
        # Robust text tag setup
        target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
        target.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        target.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        target.tag_configure("underline", underline=1)

    def _configure_tags(self):
        self.todo_tree.tag_configure("completed", foreground='gray') 
        self.todo_tree.tag_configure("High", foreground='#e74c3c') 
        self.todo_tree.tag_configure("Medium", foreground='#f39c12') 
        self.todo_tree.tag_configure("Low", foreground='#2ecc71') 
        self.todo_tree.tag_configure("overdue", foreground='#c0392b', background='#fadbd8')

    # --- Logic Implementation ---

    def update_stats(self):
        total = len(self.todo_list)
        active = sum(1 for t in self.todo_list if not t.get("completed"))
        
        # Calculate overdue
        overdue = 0
        now = datetime.now()
        for t in self.todo_list:
            if not t.get("completed") and t.get("due_datetime"):
                try:
                    dt = datetime.strptime(t["due_datetime"], DATETIME_FORMAT)
                    if dt < now:
                        overdue += 1
                except: pass
        
        self.stats_label.config(text=f"Total: {total}  |  Active: {active}  |  Overdue: {overdue}")

    def on_search_change(self, *args):
        self.search_query = self.search_var.get().lower()
        self.apply_filters_and_sort()

    def apply_filters_and_sort(self):
        self.current_filter = self.filter_var.get()
        self.current_sort = self.sort_var.get()
        now = datetime.now()

        # 1. Filter List
        filtered = []
        for i, todo in enumerate(self.todo_list):
            # Search Filter
            if self.search_query:
                text_content = todo['title'].lower()
                # Check description (simplified)
                desc_lines = todo.get("description_content", [])
                desc_text = " ".join([x['text'] for x in desc_lines]).lower()
                if self.search_query not in text_content and self.search_query not in desc_text:
                    continue

            # Status Filter
            if self.current_filter == "Active" and todo.get("completed"): continue
            if self.current_filter == "Completed" and not todo.get("completed"): continue
            if self.current_filter == "Overdue":
                is_ov = False
                if todo.get("due_datetime") and not todo.get("completed"):
                    try:
                        if datetime.strptime(todo["due_datetime"], DATETIME_FORMAT) < now: is_ov = True
                    except: pass
                if not is_ov: continue
            
            filtered.append((i, todo))

        # 2. Sort List
        def get_sort_key(item):
            todo = item[1]
            if self.current_sort == "Priority":
                p_map = {"High": 0, "Medium": 1, "Low": 2}
                return p_map.get(todo.get("priority", "Medium"), 1)
            elif self.current_sort == "Due Date":
                return todo.get("due_datetime", "9999-12-31")
            elif self.current_sort == "Created":
                return todo.get("created_at", "")
            return ""

        filtered.sort(key=get_sort_key)
        # Always put completed at bottom
        filtered.sort(key=lambda x: x[1].get("completed", False))

        self.refresh_tree(filtered)
        self.update_stats()

    def refresh_tree(self, indexed_list):
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)

        for idx, todo in indexed_list:
            # Main Status
            status = "Done" if todo.get("completed") else "Active"
            if status == "Active" and self._is_overdue(todo): status = "Overdue"
            
            # Progress calculation
            subs = todo.get("sub_todos", [])
            progress = "0%"
            if subs:
                done_subs = sum(1 for s in subs if s.get("completed"))
                pct = int((done_subs / len(subs)) * 100)
                progress = f"{pct}%"
            
            # Display Date
            d_str = todo.get("due_datetime", "")
            try:
                d_disp = datetime.strptime(d_str, DATETIME_FORMAT).strftime("%Y-%m-%d %H:%M")
            except: d_disp = ""

            tags = [todo.get("priority", "Medium")]
            if todo.get("completed"): tags.append("completed")
            elif status == "Overdue": tags.append("overdue")

            parent_id = str(idx)
            self.todo_tree.insert("", END, iid=parent_id, text=todo['title'], 
                                  values=(todo.get("priority"), d_disp, progress, status), tags=tags)

            # Subtasks
            for sub_idx, sub in enumerate(subs):
                sub_id = f"{parent_id}-{sub_idx}"
                st_tags = ["completed"] if sub.get("completed") else []
                self.todo_tree.insert(parent_id, END, iid=sub_id, text=f"↳ {sub['title']}",
                                      values=("", "", "", "Done" if sub.get("completed") else "Active"), tags=st_tags)
            
            if subs: self.todo_tree.item(parent_id, open=True)

    def _is_overdue(self, todo):
        if not todo.get("due_datetime"): return False
        try:
            return datetime.strptime(todo["due_datetime"], DATETIME_FORMAT) < datetime.now()
        except: return False

    # --- Input Handling (Simplified) ---
    def validate_time(self, P):
        if P == "" or re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", P) or re.match(r"^\d{0,2}:?\d{0,2}$", P): return True
        return False

    def toggle_reminder_options(self):
        if self.set_reminder_var.get() and not self.editing_sub_todo_mode.get():
            self.reminder_frame.pack(side=LEFT, padx=5)
        else:
            self.reminder_frame.pack_forget()

    def toggle_recurring_options(self):
        if self.set_recurring_var.get() and not self.editing_sub_todo_mode.get():
            self.recurring_combo.pack(side=LEFT, padx=5)
        else:
            self.recurring_combo.pack_forget()

    def get_formatted_text(self):
        target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
        return [{'text': target.get("1.0", "end-1c"), 'formatting': []}]

    def collect_data(self, is_sub=False):
        title = self.todo_title_entry.get().strip()
        if not title:
            messagebox.showerror("Validation Error", "Title is required")
            return None

        data = {
            "title": title,
            "description_content": self.get_formatted_text(),
            "completed": self.completed_var.get()
        }

        if not is_sub:
            data["priority"] = self.priority_var.get()
            
            d_date_str = self.due_date_entry.entry.get()
            if not d_date_str:
                messagebox.showerror("Validation Error", "Due Date is required")
                return None
                
            try:
                d_date = datetime.strptime(d_date_str, DATE_FORMAT).date()
            except ValueError:
                messagebox.showerror("Error", "Invalid Date Format")
                return None

            d_time = self.due_time_entry.get().strip() or "23:59"
            try:
                data["due_datetime"] = datetime.combine(d_date, datetime.strptime(d_time, "%H:%M").time()).strftime(DATETIME_FORMAT)
            except:
                messagebox.showerror("Error", "Invalid Time Format (HH:MM)")
                return None

            data["has_reminder"] = self.set_reminder_var.get()
            if data["has_reminder"]:
                r_date_str = self.reminder_date_entry.entry.get()
                r_time = self.reminder_time_entry.get().strip()
                if not r_time or not r_date_str: 
                    messagebox.showerror("Error", "Reminder date and time required")
                    return None
                try:
                    r_date = datetime.strptime(r_date_str, DATE_FORMAT).date()
                    data["reminder_datetime"] = datetime.combine(r_date, datetime.strptime(r_time, "%H:%M").time()).strftime(DATETIME_FORMAT)
                except: return None
            else:
                data["reminder_datetime"] = None
            
            data["is_recurring"] = self.set_recurring_var.get()
            data["recurring_frequency"] = self.recurring_combo.get() if data["is_recurring"] else "None"

        return data

    def add_new_todo(self):
        if self.editing_sub_todo_mode.get():
            self.save_sub_todo()
            return

        data = self.collect_data(is_sub=False)
        if data:
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["sub_todos"] = []
            self.todo_list.append(data)
            self.save_todos()
            self.apply_filters_and_sort()
            self.clear_form()
            self.schedule_reminder(data)

    def save_sub_todo(self):
        data = self.collect_data(is_sub=True)
        if data and self.selected_main_todo_index is not None:
            parent = self.todo_list[self.selected_main_todo_index]
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parent["sub_todos"].append(data)
            self.save_todos()
            self.apply_filters_and_sort()
            self.clear_form()

    def update_selected_todo(self):
        if self.selected_main_todo_index is None: return

        if self.editing_sub_todo_mode.get() and self.selected_sub_todo_index is not None:
             # Update Sub
             data = self.collect_data(is_sub=True)
             if data:
                 parent = self.todo_list[self.selected_main_todo_index]
                 old_sub = parent["sub_todos"][self.selected_sub_todo_index]
                 data["created_at"] = old_sub.get("created_at")
                 parent["sub_todos"][self.selected_sub_todo_index] = data
                 self.save_todos()
                 self.apply_filters_and_sort()
                 self.clear_form()
        else:
            # Update Main
            data = self.collect_data(is_sub=False)
            if data:
                old = self.todo_list[self.selected_main_todo_index]
                data["created_at"] = old.get("created_at")
                data["sub_todos"] = old.get("sub_todos", [])
                
                self.todo_list[self.selected_main_todo_index] = data
                self.save_todos()
                self.apply_filters_and_sort()
                self.clear_form()

    def delete_todo(self):
        sel = self.todo_tree.selection()
        if not sel: return
        iid = sel[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            if "-" in iid:
                main, sub = map(int, iid.split("-"))
                del self.todo_list[main]["sub_todos"][sub]
            else:
                del self.todo_list[int(iid)]
            
            self.save_todos()
            self.apply_filters_and_sort()
            self.clear_form()

    def enter_sub_todo_mode(self):
        sel = self.todo_tree.selection()
        if not sel or "-" in sel[0]:
            messagebox.showwarning("Warning", "Select a Main Task first")
            return
        
        self.selected_main_todo_index = int(sel[0])
        parent_title = self.todo_list[self.selected_main_todo_index]['title']
        
        self.clear_form(soft=True)
        self.editing_sub_todo_mode.set(True)
        self.form_header.config(text=f"Adding Sub-Task to: {parent_title}", bootstyle="info")
        
        self.priority_combo.config(state=DISABLED)
        self.due_date_entry.entry.config(state=DISABLED)
        self.due_date_entry.button.config(state=DISABLED)
        self.due_time_entry.config(state=DISABLED)
        self.advanced_group.pack_forget() 

        self.add_button.config(text="Add Sub-Task", bootstyle="info")

    def clear_form(self, soft=False):
        self.editing_sub_todo_mode.set(False)
        self.selected_sub_todo_index = None
        if not soft: self.selected_main_todo_index = None
        
        self.form_header.config(text="New Task", bootstyle="primary")
        self.todo_title_entry.delete(0, END)
        
        # Clear description robustly
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

    def on_select_todo(self, event):
        sel = self.todo_tree.selection()
        if not sel: return
        iid = sel[0]

        self.clear_form(soft=True) 
        
        if "-" in iid: # Subtask
            main_idx, sub_idx = map(int, iid.split("-"))
            self.selected_main_todo_index = main_idx
            self.selected_sub_todo_index = sub_idx
            self.editing_sub_todo_mode.set(True)
            
            todo = self.todo_list[main_idx]["sub_todos"][sub_idx]
            self.form_header.config(text="Edit Sub-Task", bootstyle="warning")
            
            self.advanced_group.pack_forget()
            
            self.due_date_entry.entry.config(state=DISABLED)
            self.due_date_entry.button.config(state=DISABLED)

            self.priority_combo.config(state=DISABLED)
            self.due_time_entry.config(state=DISABLED)

        else: # Main Task
            self.selected_main_todo_index = int(iid)
            todo = self.todo_list[int(iid)]
            self.form_header.config(text="Edit Task", bootstyle="warning")

            self.priority_var.set(todo.get("priority", "Medium"))
            if todo.get("due_datetime"):
                try:
                    dt = datetime.strptime(todo["due_datetime"], DATETIME_FORMAT)
                    self.due_date_entry.entry.delete(0, END)
                    self.due_date_entry.entry.insert(0, dt.strftime(DATE_FORMAT))
                    self.due_time_entry.insert(0, dt.strftime("%H:%M"))
                except: pass
            
            self.set_reminder_var.set(todo.get("has_reminder", False))
            if todo.get("has_reminder") and todo.get("reminder_datetime"):
                 try:
                    rdt = datetime.strptime(todo["reminder_datetime"], DATETIME_FORMAT)
                    self.reminder_date_entry.entry.delete(0, END)
                    self.reminder_date_entry.entry.insert(0, rdt.strftime(DATE_FORMAT))
                    self.reminder_time_entry.insert(0, rdt.strftime("%H:%M"))
                 except: pass
            self.toggle_reminder_options()

            self.set_recurring_var.set(todo.get("is_recurring", False))
            if todo.get("is_recurring"): self.recurring_combo.set(todo.get("recurring_frequency"))
            self.toggle_recurring_options()

        self.todo_title_entry.insert(0, todo["title"])
        self.completed_var.set(todo.get("completed", False))
        
        desc = todo.get("description_content", [])
        if desc and isinstance(desc, list):
            target = self.description_text.text if hasattr(self.description_text, 'text') else self.description_text
            for line in desc: target.insert(END, line.get('text', '') + "\n")
        
        self.add_button.config(state=DISABLED)
        self.update_button.config(state=NORMAL)

    def export_to_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if not file_path: return

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Title", "Priority", "Due Date", "Status", "Description"])
                
                for todo in self.todo_list:
                    desc = " ".join([l.get('text','') for l in todo.get("description_content", [])])
                    writer.writerow(["Main", todo['title'], todo.get('priority'), todo.get('due_datetime'), "Done" if todo.get('completed') else "Active", desc])
                    for sub in todo.get("sub_todos", []):
                        sub_desc = " ".join([l.get('text','') for l in sub.get("description_content", [])])
                        writer.writerow(["Sub", sub['title'], "-", "-", "Done" if sub.get('completed') else "Active", sub_desc])
            
            messagebox.showinfo("Export Success", f"Exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def save_todos(self):
        with open(TODO_FILE, "w") as f: json.dump(self.todo_list, f, indent=2)

    def load_todos(self):
        try:
            with open(TODO_FILE, "r") as f: 
                self.todo_list = json.load(f)
                self.apply_filters_and_sort()
        except: self.todo_list = []
        self.update_stats()

    def schedule_reminder(self, todo):
        pass 

    def on_close(self):
        if messagebox.askyesno("Exit", "Save and Quit?"):
            self.save_todos()
            self.destroy()

if __name__ == "__main__":
    app = TodoListApp()
    app.place_window_center()
    app.mainloop()