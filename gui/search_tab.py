"""
Search and filter tab for insurance claims
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List
import csv
from datetime import datetime

from gui.components import DatePicker
from utils.export import ExportManager

class SearchTab:
    def __init__(self, parent, db_manager, main_window):
        """Initialize the search tab"""
        self.parent = parent
        self.db_manager = db_manager
        self.main_window = main_window
        self.export_manager = ExportManager()
        
        # Search criteria
        self.companies = [
            "", "NIVA", "HDFC", "TATA", "CARE", "NEW INDIA", 
            "NATIONAL", "UNITED", "ORIENTAL", "FUTURE GENERALI"
        ]
        
        self.claim_statuses = [
            "", "Intimation", "Submitted", "Approved", "Declined", 
            "Reconsideration", "Settled", "Additional requirement", "Ombudsman"
        ]
        
        self.claim_types = [
            "", "Cashless", "Reimbursement", "Pre-post", "Day care", 
            "Hospital cash", "Health check-up"
        ]
        
        self.create_widgets()
        self.load_all_claims()
    
    def create_widgets(self):
        """Create the search interface"""
        self.frame = ttk.Frame(self.parent)
        
        # Search criteria frame
        search_frame = ttk.LabelFrame(self.frame, text="Search Criteria", padding="15")
        search_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Configure grid
        for i in range(6):
            search_frame.columnconfigure(i, weight=1)
        
        row = 0
        
        # Customer Name and Policy Number
        ttk.Label(search_frame, text="Customer Name:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.search_customer_name = ttk.Entry(search_frame, width=20)
        self.search_customer_name.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)
        
        ttk.Label(search_frame, text="Policy Number:").grid(row=row, column=2, sticky="w", padx=(0, 5), pady=5)
        self.search_policy_number = ttk.Entry(search_frame, width=20)
        self.search_policy_number.grid(row=row, column=3, sticky="ew", padx=(0, 15), pady=5)
        
        ttk.Label(search_frame, text="Claim Status:").grid(row=row, column=4, sticky="w", padx=(0, 5), pady=5)
        self.search_claim_status = ttk.Combobox(search_frame, values=self.claim_statuses, state="readonly")
        self.search_claim_status.grid(row=row, column=5, sticky="ew", pady=5)
        
        row += 1
        
        # Company, Claim Type
        ttk.Label(search_frame, text="Company:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.search_company = ttk.Combobox(search_frame, values=self.companies, state="readonly")
        self.search_company.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)
        
        ttk.Label(search_frame, text="Claim Type:").grid(row=row, column=2, sticky="w", padx=(0, 5), pady=5)
        self.search_claim_type = ttk.Combobox(search_frame, values=self.claim_types, state="readonly")
        self.search_claim_type.grid(row=row, column=3, sticky="ew", padx=(0, 15), pady=5)
        
        row += 1
        
        # Date ranges
        ttk.Label(search_frame, text="Entry Date From:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.search_entry_date_from = DatePicker(search_frame, allow_empty=True)
        self.search_entry_date_from.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)
        
        ttk.Label(search_frame, text="Entry Date To:").grid(row=row, column=2, sticky="w", padx=(0, 5), pady=5)
        self.search_entry_date_to = DatePicker(search_frame, allow_empty=True)
        self.search_entry_date_to.grid(row=row, column=3, sticky="ew", padx=(0, 15), pady=5)
        
        ttk.Label(search_frame, text="Admission Date From:").grid(row=row, column=4, sticky="w", padx=(0, 5), pady=5)
        self.search_admission_date_from = DatePicker(search_frame, allow_empty=True)
        self.search_admission_date_from.grid(row=row, column=5, sticky="ew", pady=5)
        
        row += 1
        
        ttk.Label(search_frame, text="Admission Date To:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.search_admission_date_to = DatePicker(search_frame, allow_empty=True)
        self.search_admission_date_to.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)
        
        # Search buttons
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=row, column=2, columnspan=4, sticky="e", pady=5)
        
        ttk.Button(button_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Show All", command=self.load_all_claims).pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Search Results", padding="15")
        results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Results count
        self.results_count_var = tk.StringVar()
        ttk.Label(results_frame, textvariable=self.results_count_var).pack(anchor="w", pady=(0, 10))
        
        # Create treeview for results
        columns = (
            'ID', 'Entry Date', 'Customer Name', 'Policy Number', 'Hospital Name',
            'Company', 'Claim Number', 'Status', 'Type', 'Claimed Amount', 'Approved Amount'
        )
        
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {
            'ID': 50, 'Entry Date': 100, 'Customer Name': 150, 'Policy Number': 120,
            'Hospital Name': 150, 'Company': 100, 'Claim Number': 120, 'Status': 100,
            'Type': 100, 'Claimed Amount': 120, 'Approved Amount': 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill="y")
        h_scrollbar.pack(side=tk.BOTTOM, fill="x")
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', self.edit_selected_claim)
        
        # Context menu
        self.create_context_menu()
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Export buttons
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(export_frame, text="Export to Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT)
        
        # Bind search on Enter key
        self.search_customer_name.bind('<Return>', lambda e: self.perform_search())
        self.search_policy_number.bind('<Return>', lambda e: self.perform_search())
    
    def create_context_menu(self):
        """Create context menu for the treeview"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit Claim", command=self.edit_selected_claim)
        self.context_menu.add_command(label="View Linked Claims", command=self.view_linked_claims)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Claim", command=self.delete_selected_claim)
    
    def show_context_menu(self, event):
        """Show context menu"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_search_filters(self) -> Dict:
        """Get current search filters"""
        filters = {}
        
        if self.search_customer_name.get().strip():
            filters['customer_name'] = self.search_customer_name.get().strip()
        
        if self.search_policy_number.get().strip():
            filters['policy_number'] = self.search_policy_number.get().strip()
        
        if self.search_claim_status.get():
            filters['claim_status'] = self.search_claim_status.get()
        
        if self.search_claim_type.get():
            filters['claim_type'] = self.search_claim_type.get()
        
        if self.search_company.get():
            filters['company_name'] = self.search_company.get()
        
        if self.search_entry_date_from.get_date():
            filters['entry_date_from'] = self.search_entry_date_from.get_date()
        
        if self.search_entry_date_to.get_date():
            filters['entry_date_to'] = self.search_entry_date_to.get_date()
        
        if self.search_admission_date_from.get_date():
            filters['admission_date_from'] = self.search_admission_date_from.get_date()
        
        if self.search_admission_date_to.get_date():
            filters['admission_date_to'] = self.search_admission_date_to.get_date()
        
        return filters
    
    def perform_search(self):
        """Perform search with current filters"""
        try:
            filters = self.get_search_filters()
            claims = self.db_manager.search_claims(filters)
            self.populate_results(claims)
            
            # Update results count
            filter_text = " (filtered)" if filters else ""
            self.results_count_var.set(f"Found {len(claims)} claim(s){filter_text}")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search claims: {str(e)}")
    
    def load_all_claims(self):
        """Load all claims"""
        try:
            claims = self.db_manager.get_all_claims()
            self.populate_results(claims)
            self.results_count_var.set(f"Showing all {len(claims)} claim(s)")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load claims: {str(e)}")
    
    def populate_results(self, claims: List[Dict]):
        """Populate the treeview with search results"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add claims to treeview
        for claim in claims:
            # Format amounts
            claimed_amount = f"₹{claim['claimed_amount']:,.2f}" if claim['claimed_amount'] else ""
            approved_amount = f"₹{claim['approved_amount']:,.2f}" if claim['approved_amount'] else ""
            
            # Format entry date
            entry_date = claim['entry_date']
            if isinstance(entry_date, str) and len(entry_date) > 10:
                entry_date = entry_date[:10]  # Take only date part
            
            values = (
                claim['id'],
                entry_date,
                claim['customer_name'],
                claim['policy_number'],
                claim['hospital_name'],
                claim['company_name'],
                claim['claim_number'] or '',
                claim['claim_status'],
                claim['claim_type'],
                claimed_amount,
                approved_amount
            )
            
            # Add item with tag for styling
            item_id = self.tree.insert('', 'end', values=values)
            
            # Color code based on status
            if claim['claim_status'] == 'Approved':
                self.tree.set(item_id, 'Status', claim['claim_status'])
                self.tree.item(item_id, tags=('approved',))
            elif claim['claim_status'] == 'Declined':
                self.tree.item(item_id, tags=('declined',))
            elif claim['claim_status'] == 'Settled':
                self.tree.item(item_id, tags=('settled',))
        
        # Configure tags
        self.tree.tag_configure('approved', background='#d4edda')
        self.tree.tag_configure('declined', background='#f8d7da')
        self.tree.tag_configure('settled', background='#cce5ff')
    
    def clear_search(self):
        """Clear all search filters"""
        self.search_customer_name.delete(0, tk.END)
        self.search_policy_number.delete(0, tk.END)
        self.search_claim_status.set("")
        self.search_claim_type.set("")
        self.search_company.set("")
        self.search_entry_date_from.set_date("")
        self.search_entry_date_to.set_date("")
        self.search_admission_date_from.set_date("")
        self.search_admission_date_to.set_date("")
    
    def sort_column(self, col):
        """Sort treeview by column"""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Determine if sorting by numeric values
        numeric_cols = ['ID', 'Claimed Amount', 'Approved Amount']
        if col in numeric_cols:
            # Sort numerically
            try:
                data.sort(key=lambda x: float(str(x[0]).replace('₹', '').replace(',', '')) if x[0] else 0)
            except ValueError:
                data.sort()  # Fall back to string sort
        else:
            data.sort()
        
        # Rearrange items
        for idx, (val, child) in enumerate(data):
            self.tree.move(child, '', idx)
    
    def edit_selected_claim(self, event=None):
        """Edit the selected claim"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a claim to edit.")
            return
        
        item = selection[0]
        claim_id = int(self.tree.item(item)['values'][0])
        self.main_window.edit_claim(claim_id)
    
    def view_linked_claims(self):
        """View claims linked to the selected claim"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a claim to view linked claims.")
            return
        
        item = selection[0]
        claim_id = int(self.tree.item(item)['values'][0])
        
        linked_claims = self.db_manager.get_linked_claims(claim_id)
        
        if not linked_claims:
            messagebox.showinfo("Linked Claims", "No linked claims found for this claim.")
            return
        
        # Create window to show linked claims
        linked_window = tk.Toplevel(self.frame)
        linked_window.title("Linked Claims")
        linked_window.geometry("800x400")
        linked_window.transient(self.main_window.root)
        linked_window.grab_set()
        
        # Create treeview for linked claims
        columns = ('ID', 'Customer Name', 'Policy Number', 'Claim Type', 'Status', 'Amount')
        linked_tree = ttk.Treeview(linked_window, columns=columns, show='headings')
        
        for col in columns:
            linked_tree.heading(col, text=col)
            linked_tree.column(col, width=120)
        
        # Populate linked claims
        for claim in linked_claims:
            amount = f"₹{claim['claimed_amount']:,.2f}" if claim['claimed_amount'] else ""
            values = (
                claim['id'],
                claim['customer_name'],
                claim['policy_number'],
                claim['claim_type'],
                claim['claim_status'],
                amount
            )
            linked_tree.insert('', 'end', values=values)
        
        linked_tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Close button
        ttk.Button(linked_window, text="Close", command=linked_window.destroy).pack(pady=10)
    
    def delete_selected_claim(self):
        """Delete the selected claim"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a claim to delete.")
            return
        
        item = selection[0]
        claim_id = int(self.tree.item(item)['values'][0])
        customer_name = self.tree.item(item)['values'][2]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the claim for {customer_name}?\n\n"
                              "This will also delete any linked claims and cannot be undone."):
            try:
                success = self.db_manager.delete_claim(claim_id)
                if success:
                    self.tree.delete(item)
                    self.main_window.set_status("Claim deleted successfully")
                    messagebox.showinfo("Success", "Claim deleted successfully.")
                else:
                    messagebox.showerror("Error", "Failed to delete claim.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete claim: {str(e)}")
    
    def export_to_excel(self):
        """Export current results to Excel"""
        claims = self.get_current_results()
        if not claims:
            messagebox.showwarning("No Data", "No claims to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.export_manager.export_to_excel(claims, filename)
                messagebox.showinfo("Export Success", f"Claims exported successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export to Excel: {str(e)}")
    
    def export_to_csv(self):
        """Export current results to CSV"""
        claims = self.get_current_results()
        if not claims:
            messagebox.showwarning("No Data", "No claims to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.export_manager.export_to_csv(claims, filename)
                messagebox.showinfo("Export Success", f"Claims exported successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export to CSV: {str(e)}")
    
    def get_current_results(self) -> List[Dict]:
        """Get current results as a list of dictionaries"""
        claims = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            claim_id = values[0]
            
            # Get full claim data from database
            claim = self.db_manager.get_claim_by_id(claim_id)
            if claim:
                claims.append(claim)
        
        return claims
    
    def export_claims(self, claims: List[Dict]):
        """Export given claims list"""
        if not claims:
            messagebox.showwarning("No Data", "No claims to export.")
            return
        
        # Ask user for format
        export_format = messagebox.askyesno("Export Format", "Export to Excel? (No = CSV)")
        
        if export_format:
            filename = filedialog.asksaveasfilename(
                title="Export to Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                try:
                    self.export_manager.export_to_excel(claims, filename)
                    messagebox.showinfo("Export Success", f"Claims exported successfully to {filename}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export to Excel: {str(e)}")
        else:
            filename = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                try:
                    self.export_manager.export_to_csv(claims, filename)
                    messagebox.showinfo("Export Success", f"Claims exported successfully to {filename}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export to CSV: {str(e)}")
