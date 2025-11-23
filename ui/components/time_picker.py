"""Time picker widget with hour and minute spinboxes."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class TimePicker(ttk.Frame):
    """Time picker with hour and minute selection."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        
        # Hour spinbox (00-23)
        self.hour_var = tk.StringVar(value="12")
        self.hour_spin = ttk.Spinbox(
            self,
            from_=0,
            to=23,
            textvariable=self.hour_var,
            width=3,
            wrap=True,
            format="%02.0f"
        )
        self.hour_spin.pack(side=LEFT)
        
        # Separator
        ttk.Label(self, text=":").pack(side=LEFT, padx=2)
        
        # Minute spinbox (00-59)
        self.minute_var = tk.StringVar(value="00")
        self.minute_spin = ttk.Spinbox(
            self,
            from_=0,
            to=59,
            textvariable=self.minute_var,
            width=3,
            wrap=True,
            format="%02.0f"
        )
        self.minute_spin.pack(side=LEFT)
    
    def get(self):
        """Get time in HH:MM format."""
        try:
            hour = int(float(self.hour_var.get()))
            minute = int(float(self.minute_var.get()))
            return f"{hour:02d}:{minute:02d}"
        except:
            return "12:00"
    
    def set(self, time_str):
        """Set time from HH:MM format."""
        try:
            if time_str and ":" in time_str:
                hour, minute = time_str.split(":")
                self.hour_var.set(f"{int(hour):02d}")
                self.minute_var.set(f"{int(minute):02d}")
        except:
            pass
    
    def delete(self, start, end):
        """Clear the time picker."""
        self.hour_var.set("12")
        self.minute_var.set("00")
    
    def insert(self, index, value):
        """Insert time value."""
        self.set(value)
    
    def config(self, **kwargs):
        """Configure the time picker."""
        state = kwargs.get('state')
        if state:
            self.hour_spin.config(state=state)
            self.minute_spin.config(state=state)
