#!/usr/bin/env python3
"""
Insurance Claim Management System
Main entry point for the desktop application
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Create and run the main application
        root = tk.Tk()
        app = MainWindow(root, db_manager)
        
        # Configure window close behavior
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit the Insurance Claim Management System?"):
                db_manager.close()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
