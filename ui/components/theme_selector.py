"""Theme selector component."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config.themes import THEMES, get_theme_names


class ThemeSelector(ttk.Frame):
    """Theme selector dropdown component."""
    
    def __init__(self, parent, current_theme, on_theme_change):
        super().__init__(parent)
        self.on_theme_change = on_theme_change
        
        # Theme selector label
        ttk.Label(self, text="🎨 Theme:").pack(side=LEFT, padx=(0, 5))
        
        # Theme dropdown
        self.theme_var = tk.StringVar(value=current_theme)
        
        # Create display names for themes
        theme_display = [f"{THEMES[name]['name']} ({THEMES[name]['type'].title()})" 
                        for name in get_theme_names()]
        theme_names = get_theme_names()
        
        self.theme_combo = ttk.Combobox(
            self, 
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=15
        )
        self.theme_combo.pack(side=LEFT, padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_select)
        
        # Apply button
        self.apply_btn = ttk.Button(
            self, 
            text="Apply Theme",
            command=self._apply_theme,
            bootstyle="info-outline"
        )
        self.apply_btn.pack(side=LEFT, padx=5)
    
    def _on_select(self, event=None):
        """Handle theme selection."""
        pass  # Just update the variable
    
    def _apply_theme(self):
        """Apply the selected theme."""
        selected_theme = self.theme_var.get()
        if self.on_theme_change:
            self.on_theme_change(selected_theme)
    
    def set_theme(self, theme_name):
        """Set the current theme."""
        self.theme_var.set(theme_name)
