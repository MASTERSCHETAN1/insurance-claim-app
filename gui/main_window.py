"""
Main window for Insurance Claim Management System
Contains the primary GUI layout and tab management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from gui.claim_form import ClaimFormTab
from gui.search_tab import SearchTab
from database import DatabaseManager

class MainWindow:
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        """Initialize the main application window"""
        self.root = root
        self.db_manager = db_manager
        
        self.setup_window()
        self.create_widgets()
        self.setup_menu()
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Insurance Claim Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """Create the main interface widgets"""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Insurance Claim Management System",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Create tabs
        self.claim_form_tab = ClaimFormTab(self.notebook, self.db_manager, self)
        self.search_tab = SearchTab(self.notebook, self.db_manager, self)
        
        # Add tabs to notebook
        self.notebook.add(self.claim_form_tab.frame, text="New/Edit Claim")
        self.notebook.add(self.search_tab.frame, text="Search Claims")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    
    def setup_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Claim", command=self.new_claim, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export All Claims...", command=self.export_all_claims)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Claims List", command=self.show_search_tab)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_claim())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def new_claim(self):
        """Switch to new claim tab and reset form"""
        self.notebook.select(0)
        self.claim_form_tab.reset_form()
    
    def show_search_tab(self):
        """Switch to search tab"""
        self.notebook.select(1)
    
    def export_all_claims(self):
        """Export all claims to file"""
        claims = self.db_manager.get_all_claims()
        if claims:
            self.search_tab.export_claims(claims)
        else:
            messagebox.showinfo("Export", "No claims to export.")
    
    def show_statistics(self):
        """Show claim statistics in a popup"""
        stats = self.db_manager.get_claim_statistics()
        
        # Create statistics window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Claim Statistics")
        stats_window.geometry("400x300")
        stats_window.resizable(False, False)
        
        # Center the window
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Claim Statistics", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Total claims
        ttk.Label(main_frame, text=f"Total Claims: {stats['total_claims']}", font=('Arial', 12)).pack(anchor=tk.W)
        
        # Financial summary
        ttk.Label(main_frame, text=f"Total Claimed Amount: ₹{stats['total_claimed']:,.2f}", font=('Arial', 12)).pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(main_frame, text=f"Total Approved Amount: ₹{stats['total_approved']:,.2f}", font=('Arial', 12)).pack(anchor=tk.W, pady=(5, 20))
        
        # Claims by status
        if stats['by_status']:
            ttk.Label(main_frame, text="Claims by Status:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            for status, count in stats['by_status'].items():
                ttk.Label(main_frame, text=f"  {status}: {count}").pack(anchor=tk.W)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=stats_window.destroy).pack(pady=(20, 0))
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Insurance Claim Management System\n\n"
            "Version 1.0\n"
            "A comprehensive desktop application for managing insurance claims.\n\n"
            "Features:\n"
            "• Local SQLite database storage\n"
            "• Comprehensive claim entry and editing\n"
            "• Advanced search and filtering\n"
            "• Data export capabilities\n"
            "• Claim linking system"
        )
    
    def set_status(self, message: str):
        """Update the status bar"""
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set("Ready"))
    
    def edit_claim(self, claim_id: int):
        """Load a claim for editing"""
        claim_data = self.db_manager.get_claim_by_id(claim_id)
        if claim_data:
            self.notebook.select(0)
            self.claim_form_tab.load_claim(claim_data)
        else:
            messagebox.showerror("Error", "Claim not found.")
    
    def refresh_search(self):
        """Refresh the search results"""
        if hasattr(self.search_tab, 'perform_search'):
            self.search_tab.perform_search()
