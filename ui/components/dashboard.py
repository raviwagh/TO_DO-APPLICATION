"""Dashboard component with stats and search."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from config.settings import DATETIME_FORMAT


class Dashboard(ttk.Frame):
    """Dashboard showing statistics and search bar."""
    
    def __init__(self, parent, on_search_change, on_export):
        super().__init__(parent, padding=10)
        self.on_search_change = on_search_change
        self.on_export = on_export
        
        # Stats label
        self.stats_label = ttk.Label(
            self, 
            text="Total: 0 | Active: 0 | Overdue: 0",
            font=("Helvetica", 12, "bold"),
            bootstyle="info"
        )
        self.stats_label.pack(side=LEFT, padx=10)
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(side=RIGHT)
        
        ttk.Label(search_frame, text="🔍").pack(side=LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search_change(self.search_var.get()))
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=LEFT)
        
        # Export button
        ttk.Button(
            self, 
            text="Export CSV",
            command=self.on_export,
            bootstyle="outline-secondary"
        ).pack(side=RIGHT, padx=20)
    
    def update_stats(self, todos):
        """Update statistics display."""
        total = len(todos)
        active = sum(1 for t in todos if not t.get("completed"))
        completed = sum(1 for t in todos if t.get("completed"))
        
        # Calculate overdue
        overdue = 0
        now = datetime.now()
        for t in todos:
            if not t.get("completed") and t.get("due_datetime"):
                try:
                    dt = datetime.strptime(t["due_datetime"], DATETIME_FORMAT)
                    if dt < now:
                        overdue += 1
                except:
                    pass
        
        # Enhanced stats with emojis
        stats_text = f"📊 Total: {total}  |  ✅ Active: {active}  |  ⏰ Overdue: {overdue}  |  ✓ Completed: {completed}"
        self.stats_label.config(text=stats_text)
    
    def get_search_query(self):
        """Get current search query."""
        return self.search_var.get().lower()
