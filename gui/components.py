"""
Custom GUI components for the Insurance Claim Management System
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
from typing import Optional, Union

class DatePicker(ttk.Frame):
    """Custom date picker widget"""
    
    def __init__(self, parent, default_date=None, allow_empty=False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.allow_empty = allow_empty
        
        # Create date entry
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(self, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create calendar button
        self.calendar_button = ttk.Button(self, text="📅", width=3, command=self.show_calendar)
        self.calendar_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Set default date
        if default_date:
            if isinstance(default_date, datetime):
                self.set_date(default_date.strftime('%Y-%m-%d'))
            else:
                self.set_date(default_date)
        
        # Bind validation
        self.date_entry.bind('<FocusOut>', self.validate_date)
        self.date_entry.bind('<KeyRelease>', self.format_date)
    
    def format_date(self, event=None):
        """Format date as user types"""
        text = self.date_var.get()
        if len(text) == 2 or len(text) == 5:
            if not text.endswith('/'):
                self.date_var.set(text + '/')
                self.date_entry.icursor(len(text) + 1)
    
    def validate_date(self, event=None):
        """Validate and format the date"""
        text = self.date_var.get().strip()
        
        if not text and self.allow_empty:
            return True
        
        if not text:
            return False
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    date_obj = datetime.strptime(text, fmt)
                    self.date_var.set(date_obj.strftime('%Y-%m-%d'))
                    return True
                except ValueError:
                    continue
            
            # If no format worked, show error
            self.date_var.set("")
            return False
            
        except Exception:
            self.date_var.set("")
            return False
    
    def show_calendar(self):
        """Show calendar popup"""
        calendar_window = tk.Toplevel(self)
        calendar_window.title("Select Date")
        calendar_window.geometry("250x220")
        calendar_window.resizable(False, False)
        calendar_window.transient(self.winfo_toplevel())
        calendar_window.grab_set()
        
        # Position calendar window
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        calendar_window.geometry(f"+{x}+{y}")
        
        # Current date
        current_date = datetime.now()
        try:
            if self.date_var.get():
                current_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
        except ValueError:
            pass
        
        # Calendar frame
        cal_frame = ttk.Frame(calendar_window, padding="10")
        cal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Month/Year selector
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cal_month_var = tk.IntVar(value=current_date.month)
        self.cal_year_var = tk.IntVar(value=current_date.year)
        
        ttk.Button(nav_frame, text="<", width=3, command=lambda: self.change_month(-1, calendar_window, cal_frame)).pack(side=tk.LEFT)
        
        month_label = ttk.Label(nav_frame, text="")
        month_label.pack(side=tk.LEFT, expand=True)
        
        ttk.Button(nav_frame, text=">", width=3, command=lambda: self.change_month(1, calendar_window, cal_frame)).pack(side=tk.RIGHT)
        
        # Calendar grid
        self.calendar_frame = ttk.Frame(cal_frame)
        self.calendar_frame.pack()
        
        # Create calendar
        self.create_calendar(calendar_window, current_date.day)
        
        # Update month label
        month_label.config(text=f"{calendar.month_name[self.cal_month_var.get()]} {self.cal_year_var.get()}")
        
        # Today button
        ttk.Button(cal_frame, text="Today", command=lambda: self.select_date(datetime.now(), calendar_window)).pack(pady=(10, 0))
    
    def create_calendar(self, calendar_window, selected_day=None):
        """Create calendar grid"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(self.calendar_frame, text=day, font=('Arial', 8, 'bold')).grid(row=0, column=i, padx=1, pady=1)
        
        # Calendar days
        cal = calendar.monthcalendar(self.cal_year_var.get(), self.cal_month_var.get())
        
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    ttk.Label(self.calendar_frame, text="").grid(row=week_num, column=day_num, padx=1, pady=1)
                else:
                    # Day button
                    btn = tk.Button(
                        self.calendar_frame, 
                        text=str(day), 
                        width=3, 
                        height=1,
                        command=lambda d=day: self.select_date(
                            datetime(self.cal_year_var.get(), self.cal_month_var.get(), d),
                            calendar_window
                        )
                    )
                    
                    # Highlight selected day
                    if day == selected_day:
                        btn.config(bg='lightblue')
                    
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1)
    
    def change_month(self, delta, calendar_window, cal_frame):
        """Change calendar month"""
        new_month = self.cal_month_var.get() + delta
        new_year = self.cal_year_var.get()
        
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1
        
        self.cal_month_var.set(new_month)
        self.cal_year_var.set(new_year)
        
        # Update month label
        for widget in cal_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and child.cget('text').count(' ') == 1:
                        child.config(text=f"{calendar.month_name[new_month]} {new_year}")
        
        # Recreate calendar
        self.create_calendar(calendar_window)
    
    def select_date(self, date, calendar_window):
        """Select a date from calendar"""
        self.date_var.set(date.strftime('%Y-%m-%d'))
        calendar_window.destroy()
    
    def get_date(self) -> str:
        """Get the current date value"""
        return self.date_var.get()
    
    def set_date(self, date: Union[str, datetime, None]):
        """Set the date value"""
        if date is None or date == "":
            self.date_var.set("")
        elif isinstance(date, datetime):
            self.date_var.set(date.strftime('%Y-%m-%d'))
        else:
            # Assume string, validate and format
            self.date_var.set(str(date))
            self.validate_date()

class CurrencyEntry(ttk.Frame):
    """Custom currency entry widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Currency symbol
        ttk.Label(self, text="₹").pack(side=tk.LEFT)
        
        # Entry field
        self.amount_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.amount_var, width=15)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind validation
        self.entry.bind('<KeyRelease>', self.format_amount)
        self.entry.bind('<FocusOut>', self.validate_amount)
    
    def format_amount(self, event=None):
        """Format amount with commas"""
        text = self.amount_var.get()
        
        # Remove non-numeric characters except decimal point
        cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
        
        try:
            # Split by decimal point
            if '.' in cleaned:
                whole, decimal = cleaned.split('.', 1)
                # Limit decimal places to 2
                decimal = decimal[:2]
                # Format with commas
                if whole:
                    formatted = f"{int(whole):,}"
                    if decimal:
                        formatted += f".{decimal}"
                    self.amount_var.set(formatted)
            else:
                if cleaned:
                    self.amount_var.set(f"{int(cleaned):,}")
        except ValueError:
            pass
    
    def validate_amount(self, event=None):
        """Validate the amount"""
        text = self.amount_var.get()
        
        if not text:
            return True
        
        try:
            # Remove commas for validation
            cleaned = text.replace(',', '')
            float(cleaned)
            return True
        except ValueError:
            self.amount_var.set("")
            return False
    
    def get_value(self) -> Optional[float]:
        """Get the numeric value"""
        text = self.amount_var.get()
        if not text:
            return None
        
        try:
            return float(text.replace(',', ''))
        except ValueError:
            return None
    
    def set_value(self, value: Optional[Union[float, int, str]]):
        """Set the value"""
        if value is None or value == "":
            self.amount_var.set("")
        else:
            try:
                num_value = float(value)
                if num_value == int(num_value):
                    self.amount_var.set(f"{int(num_value):,}")
                else:
                    self.amount_var.set(f"{num_value:,.2f}")
            except (ValueError, TypeError):
                self.amount_var.set("")

class SearchableCombobox(ttk.Combobox):
    """Combobox with search functionality"""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.all_values = values or []
        self['values'] = self.all_values
        
        # Bind events for search functionality
        self.bind('<KeyRelease>', self.on_keyrelease)
        self.bind('<Button-1>', self.on_click)
    
    def on_keyrelease(self, event):
        """Filter values based on typed text"""
        typed = self.get().lower()
        
        if typed == '':
            filtered_values = self.all_values
        else:
            filtered_values = [item for item in self.all_values if typed in item.lower()]
        
        self['values'] = filtered_values
        
        # Show dropdown if there are matches
        if filtered_values:
            self.event_generate('<Down>')
    
    def on_click(self, event):
        """Show all values on click"""
        self['values'] = self.all_values
