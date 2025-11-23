"""Task list component with treeview."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from config.settings import DATETIME_FORMAT, FILTER_OPTIONS, SORT_OPTIONS


class TaskList(ttk.Frame):
    """Task list with filtering and sorting."""
    
    def __init__(self, parent, on_select, on_delete, on_add_subtask, theme_config):
        super().__init__(parent, padding=10)
        self.on_select = on_select
        self.on_delete = on_delete
        self.on_add_subtask = on_add_subtask
        self.theme_config = theme_config
        
        # Filter controls
        self._build_filter_controls()
        
        # Treeview
        self._build_treeview()
        
        self.current_filter = "All"
        self.current_sort = "Due Date"
    
    def _build_filter_controls(self):
        """Build filter and sort controls."""
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=LEFT)
        self.filter_var = tk.StringVar(value="All")
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=FILTER_OPTIONS,
            state="readonly",
            width=10
        ).pack(side=LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Sort:").pack(side=LEFT, padx=(15, 0))
        self.sort_var = tk.StringVar(value="Due Date")
        ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=SORT_OPTIONS,
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            filter_frame,
            text="Apply",
            command=self.apply_filters,
            bootstyle="outline-primary"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            filter_frame,
            text="🗑️ Delete",
            command=self.on_delete,
            bootstyle="danger-outline"
        ).pack(side=RIGHT)
        
        ttk.Button(
            filter_frame,
            text="➕ Sub-Task",
            command=self.on_add_subtask,
            bootstyle="info-outline"
        ).pack(side=RIGHT, padx=5)
    
    def _build_treeview(self):
        """Build the treeview widget."""
        cols = ("Priority", "Due Date", "Progress", "Status")
        self.tree = ttk.Treeview(
            self,
            columns=cols,
            show='tree headings',
            selectmode='browse',
            bootstyle="primary"
        )
        
        self.tree.heading("#0", text="Task Title")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Progress", text="Progress")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("#0", width=300)
        self.tree.column("Priority", width=80, anchor=CENTER)
        self.tree.column("Due Date", width=120, anchor=CENTER)
        self.tree.column("Progress", width=80, anchor=CENTER)
        self.tree.column("Status", width=80, anchor=CENTER)
        
        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_select())
        
        vsb.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        self._configure_tags()
    
    def _configure_tags(self):
        """Configure treeview tags with theme colors."""
        colors = self.theme_config.get("colors", {})
        self.tree.tag_configure("completed", foreground=colors.get("completed", "gray"))
        self.tree.tag_configure("High", foreground=colors.get("high_priority", "#e74c3c"))
        self.tree.tag_configure("Medium", foreground=colors.get("medium_priority", "#f39c12"))
        self.tree.tag_configure("Low", foreground=colors.get("low_priority", "#2ecc71"))
        self.tree.tag_configure(
            "overdue",
            foreground=colors.get("overdue_fg", "#c0392b"),
            background=colors.get("overdue_bg", "#fadbd8")
        )
    
    def apply_filters(self):
        """Apply current filters and sorting."""
        self.current_filter = self.filter_var.get()
        self.current_sort = self.sort_var.get()
        # Trigger refresh in parent
        if hasattr(self, 'refresh_callback'):
            self.refresh_callback()
    
    def refresh(self, todos, search_query=""):
        """Refresh the treeview with filtered and sorted todos."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and sort
        filtered = self._filter_todos(todos, search_query)
        sorted_todos = self._sort_todos(filtered)
        
        # Populate tree
        for idx, todo in sorted_todos:
            self._insert_todo(idx, todo)
    
    def _filter_todos(self, todos, search_query):
        """Filter todos based on current filter and search."""
        filtered = []
        now = datetime.now()
        
        for i, todo in enumerate(todos):
            # Search filter
            if search_query:
                text_content = todo['title'].lower()
                desc_lines = todo.get("description_content", [])
                desc_text = " ".join([x.get('text', '') for x in desc_lines]).lower()
                if search_query not in text_content and search_query not in desc_text:
                    continue
            
            # Status filter
            if self.current_filter == "Active" and todo.get("completed"):
                continue
            if self.current_filter == "Completed" and not todo.get("completed"):
                continue
            if self.current_filter == "Overdue":
                is_ov = False
                if todo.get("due_datetime") and not todo.get("completed"):
                    try:
                        if datetime.strptime(todo["due_datetime"], DATETIME_FORMAT) < now:
                            is_ov = True
                    except:
                        pass
                if not is_ov:
                    continue
            
            filtered.append((i, todo))
        
        return filtered
    
    def _sort_todos(self, indexed_todos):
        """Sort todos based on current sort option."""
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
        
        sorted_list = sorted(indexed_todos, key=get_sort_key)
        # Put completed at bottom
        sorted_list.sort(key=lambda x: x[1].get("completed", False))
        return sorted_list
    
    def _insert_todo(self, idx, todo):
        """Insert a todo item into the tree."""
        # Status
        status = "Done" if todo.get("completed") else "Active"
        is_overdue = False
        if status == "Active" and todo.get("due_datetime"):
            try:
                if datetime.strptime(todo["due_datetime"], DATETIME_FORMAT) < datetime.now():
                    status = "Overdue"
                    is_overdue = True
            except:
                pass
        
        # Progress
        subs = todo.get("sub_todos", [])
        progress = "0%"
        if subs:
            done_subs = sum(1 for s in subs if s.get("completed"))
            pct = int((done_subs / len(subs)) * 100)
            progress = f"{pct}%"
        
        # Display date
        d_str = todo.get("due_datetime", "")
        try:
            d_disp = datetime.strptime(d_str, DATETIME_FORMAT).strftime("%Y-%m-%d %H:%M")
        except:
            d_disp = ""
        
        # Tags
        tags = [todo.get("priority", "Medium")]
        if todo.get("completed"):
            tags.append("completed")
        elif is_overdue:
            tags.append("overdue")
        
        # Insert main task
        parent_id = str(idx)
        self.tree.insert(
            "", END,
            iid=parent_id,
            text=todo['title'],
            values=(todo.get("priority"), d_disp, progress, status),
            tags=tags
        )
        
        # Insert subtasks
        for sub_idx, sub in enumerate(subs):
            sub_id = f"{parent_id}-{sub_idx}"
            st_tags = ["completed"] if sub.get("completed") else []
            self.tree.insert(
                parent_id, END,
                iid=sub_id,
                text=f"↳ {sub['title']}",
                values=("", "", "", "Done" if sub.get("completed") else "Active"),
                tags=st_tags
            )
        
        if subs:
            self.tree.item(parent_id, open=True)
    
    def get_selection(self):
        """Get currently selected item."""
        sel = self.tree.selection()
        if sel:
            return sel[0]
        return None
    
    def update_theme(self, theme_config):
        """Update theme colors."""
        self.theme_config = theme_config
        self._configure_tags()
