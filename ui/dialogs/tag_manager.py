"""Tag management dialog."""

import tkinter as tk
from tkinter import messagebox, colorchooser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config.settings import PREDEFINED_TAGS


class TagManagerDialog(tk.Toplevel):
    """Dialog for managing tags."""
    
    def __init__(self, parent, current_tags, on_save):
        super().__init__(parent)
        self.title("Manage Tags")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.current_tags = current_tags.copy() if current_tags else {}
        self.on_save = on_save
        
        self._build_ui()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
    
    def _build_ui(self):
        """Build the UI."""
        # Header
        header = ttk.Label(
            self,
            text="Tag Manager",
            font=("Helvetica", 16, "bold")
        )
        header.pack(pady=10)
        
        # Tag list frame
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable tag list
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=canvas.yview)
        self.tag_container = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=self.tag_container, anchor=NW)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.tag_container.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Populate with predefined tags
        all_tags = {**PREDEFINED_TAGS, **self.current_tags}
        for tag_name, color in all_tags.items():
            self._add_tag_row(tag_name, color)
        
        # Add new tag section
        add_frame = ttk.Frame(self)
        add_frame.pack(fill=X, padx=20, pady=10)
        
        ttk.Label(add_frame, text="New Tag:").pack(side=LEFT, padx=5)
        self.new_tag_entry = ttk.Entry(add_frame, width=20)
        self.new_tag_entry.pack(side=LEFT, padx=5)
        
        self.new_tag_color = "#3498db"
        self.color_btn = ttk.Button(
            add_frame,
            text="Color",
            command=self._choose_color,
            bootstyle="info"
        )
        self.color_btn.pack(side=LEFT, padx=5)
        
        ttk.Button(
            add_frame,
            text="Add Tag",
            command=self._add_new_tag,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        # Bottom buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            bootstyle="success"
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bootstyle="secondary"
        ).pack(side=RIGHT, padx=5)
    
    def _add_tag_row(self, tag_name, color):
        """Add a tag row to the list."""
        row = ttk.Frame(self.tag_container)
        row.pack(fill=X, pady=2)
        
        # Color indicator
        color_label = tk.Label(row, bg=color, width=3, height=1)
        color_label.pack(side=LEFT, padx=5)
        
        # Tag name
        ttk.Label(row, text=tag_name, font=("Helvetica", 10)).pack(side=LEFT, padx=10)
        
        # Delete button (only for custom tags)
        if tag_name not in PREDEFINED_TAGS:
            ttk.Button(
                row,
                text="✕",
                width=3,
                command=lambda: self._delete_tag(tag_name, row),
                bootstyle="danger-outline"
            ).pack(side=RIGHT, padx=5)
    
    def _choose_color(self):
        """Choose color for new tag."""
        color = colorchooser.askcolor(initialcolor=self.new_tag_color)
        if color[1]:
            self.new_tag_color = color[1]
            self.color_btn.configure(bootstyle="info")
    
    def _add_new_tag(self):
        """Add a new custom tag."""
        tag_name = self.new_tag_entry.get().strip()
        if not tag_name:
            messagebox.showwarning("Warning", "Please enter a tag name")
            return
        
        if tag_name in {**PREDEFINED_TAGS, **self.current_tags}:
            messagebox.showwarning("Warning", "Tag already exists")
            return
        
        self.current_tags[tag_name] = self.new_tag_color
        self._add_tag_row(tag_name, self.new_tag_color)
        self.new_tag_entry.delete(0, END)
    
    def _delete_tag(self, tag_name, row):
        """Delete a custom tag."""
        if messagebox.askyesno("Confirm", f"Delete tag '{tag_name}'?"):
            if tag_name in self.current_tags:
                del self.current_tags[tag_name]
            row.destroy()
    
    def _save(self):
        """Save and close."""
        self.on_save(self.current_tags)
        self.destroy()
