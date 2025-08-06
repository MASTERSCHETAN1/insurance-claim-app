"""
Claim form tab for creating and editing insurance claims
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Optional

from gui.components import DatePicker, CurrencyEntry
from utils.validators import ClaimValidator
from models.claim import Claim

class ClaimFormTab:
    def __init__(self, parent, db_manager, main_window):
        """Initialize the claim form tab"""
        self.parent = parent
        self.db_manager = db_manager
        self.main_window = main_window
        self.current_claim_id = None
        self.validator = ClaimValidator()
        
        # Company dropdown options
        self.companies = [
            "NIVA", "HDFC", "TATA", "CARE", "NEW INDIA", 
            "NATIONAL", "UNITED", "ORIENTAL", "FUTURE GENERALI"
        ]
        
        # Claim status options
        self.claim_statuses = [
            "Intimation", "Submitted", "Approved", "Declined", 
            "Reconsideration", "Settled", "Additional requirement", "Ombudsman"
        ]
        
        # Claim type options
        self.claim_types = [
            "Cashless", "Reimbursement", "Pre-post", "Day care", 
            "Hospital cash", "Health check-up"
        ]
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the claim form interface"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Create scrollable frame
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form container
        form_frame = ttk.LabelFrame(self.scrollable_frame, text="Claim Information", padding="20")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(4):
            form_frame.columnconfigure(i, weight=1)
        
        row = 0
        
        # Entry Date
        ttk.Label(form_frame, text="Entry Date:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.entry_date = DatePicker(form_frame, default_date=datetime.now())
        self.entry_date.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Admission Date
        ttk.Label(form_frame, text="Date of Admission:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.admission_date = DatePicker(form_frame)
        self.admission_date.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Customer Name
        ttk.Label(form_frame, text="Customer Name:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.customer_name = ttk.Entry(form_frame, width=30)
        self.customer_name.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Policy Number
        ttk.Label(form_frame, text="Policy Number:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.policy_number = ttk.Entry(form_frame, width=30)
        self.policy_number.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Hospital Name
        ttk.Label(form_frame, text="Hospital Name:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.hospital_name = ttk.Entry(form_frame, width=30)
        self.hospital_name.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Company Name
        ttk.Label(form_frame, text="Company Name:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.company_name = ttk.Combobox(form_frame, values=self.companies, state="readonly")
        self.company_name.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Claim Number
        ttk.Label(form_frame, text="Claim Number:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.claim_number = ttk.Entry(form_frame, width=30)
        self.claim_number.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Claim Status
        ttk.Label(form_frame, text="Claim Status:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.claim_status = ttk.Combobox(form_frame, values=self.claim_statuses, state="readonly")
        self.claim_status.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Claimed Amount
        ttk.Label(form_frame, text="Claimed Amount:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.claimed_amount = CurrencyEntry(form_frame)
        self.claimed_amount.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Approved Amount
        ttk.Label(form_frame, text="Approved Amount:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.approved_amount = CurrencyEntry(form_frame)
        self.approved_amount.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Claim Type
        ttk.Label(form_frame, text="Claim Type:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.claim_type = ttk.Combobox(form_frame, values=self.claim_types, state="readonly")
        self.claim_type.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Parent Claim (for linking)
        ttk.Label(form_frame, text="Link to Main Claim:").grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        self.parent_claim_var = tk.StringVar()
        self.parent_claim = ttk.Combobox(form_frame, textvariable=self.parent_claim_var, state="readonly")
        self.parent_claim.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Remark (spans all columns)
        ttk.Label(form_frame, text="Remark:").grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=5)
        self.remark = tk.Text(form_frame, height=4, wrap=tk.WORD)
        self.remark.grid(row=row, column=1, columnspan=3, sticky="ew", pady=5)
        
        row += 1
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=4, pady=20)
        
        # Buttons
        self.save_button = ttk.Button(button_frame, text="Save Claim", command=self.save_claim)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.reset_form)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_edit)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Bind events
        self.claim_type.bind('<<ComboboxSelected>>', self.on_claim_type_changed)
        
        # Load parent claims for linking
        self.load_parent_claims()
    
    def load_parent_claims(self):
        """Load main claims that can be used as parent claims"""
        main_claims = self.db_manager.get_main_claims()
        parent_options = [""]  # Empty option for no linking
        
        for claim in main_claims:
            display_text = f"{claim['id']} - {claim['customer_name']} ({claim['policy_number']})"
            if claim['claim_number']:
                display_text += f" - {claim['claim_number']}"
            parent_options.append(display_text)
        
        self.parent_claim['values'] = parent_options
    
    def on_claim_type_changed(self, event=None):
        """Handle claim type selection"""
        claim_type = self.claim_type.get()
        
        # Enable/disable parent claim linking based on claim type
        if claim_type in ['Pre-post', 'Hospital cash']:
            self.parent_claim['state'] = 'readonly'
        else:
            self.parent_claim['state'] = 'disabled'
            self.parent_claim_var.set("")
    
    def get_form_data(self) -> Dict:
        """Get data from form fields"""
        # Extract parent claim ID if selected
        parent_claim_id = None
        parent_text = self.parent_claim_var.get()
        if parent_text and parent_text.strip():
            try:
                parent_claim_id = int(parent_text.split(' - ')[0])
            except (ValueError, IndexError):
                parent_claim_id = None
        
        return {
            'entry_date': self.entry_date.get_date(),
            'admission_date': self.admission_date.get_date(),
            'customer_name': self.customer_name.get().strip(),
            'policy_number': self.policy_number.get().strip(),
            'hospital_name': self.hospital_name.get().strip(),
            'company_name': self.company_name.get(),
            'claim_number': self.claim_number.get().strip() or None,
            'claim_status': self.claim_status.get(),
            'claimed_amount': self.claimed_amount.get_value(),
            'approved_amount': self.approved_amount.get_value(),
            'claim_type': self.claim_type.get(),
            'remark': self.remark.get("1.0", tk.END).strip(),
            'parent_claim_id': parent_claim_id
        }
    
    def set_form_data(self, data: Dict):
        """Set form fields from data"""
        self.entry_date.set_date(data.get('entry_date', ''))
        self.admission_date.set_date(data.get('admission_date', ''))
        self.customer_name.delete(0, tk.END)
        self.customer_name.insert(0, data.get('customer_name', ''))
        self.policy_number.delete(0, tk.END)
        self.policy_number.insert(0, data.get('policy_number', ''))
        self.hospital_name.delete(0, tk.END)
        self.hospital_name.insert(0, data.get('hospital_name', ''))
        self.company_name.set(data.get('company_name', ''))
        self.claim_number.delete(0, tk.END)
        self.claim_number.insert(0, data.get('claim_number', '') or '')
        self.claim_status.set(data.get('claim_status', ''))
        self.claimed_amount.set_value(data.get('claimed_amount'))
        self.approved_amount.set_value(data.get('approved_amount'))
        self.claim_type.set(data.get('claim_type', ''))
        self.remark.delete("1.0", tk.END)
        self.remark.insert("1.0", data.get('remark', ''))
        
        # Set parent claim if exists
        if data.get('parent_claim_id'):
            parent_claim = self.db_manager.get_claim_by_id(data['parent_claim_id'])
            if parent_claim:
                display_text = f"{parent_claim['id']} - {parent_claim['customer_name']} ({parent_claim['policy_number']})"
                if parent_claim['claim_number']:
                    display_text += f" - {parent_claim['claim_number']}"
                self.parent_claim_var.set(display_text)
        
        # Trigger claim type change event
        self.on_claim_type_changed()
    
    def validate_form(self) -> bool:
        """Validate form data"""
        data = self.get_form_data()
        errors = self.validator.validate_claim(data)
        
        if errors:
            error_message = "Please correct the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Error", error_message)
            return False
        
        return True
    
    def save_claim(self):
        """Save or update the claim"""
        if not self.validate_form():
            return
        
        try:
            data = self.get_form_data()
            
            if self.current_claim_id:
                # Update existing claim
                success = self.db_manager.update_claim(self.current_claim_id, data)
                if success:
                    self.main_window.set_status("Claim updated successfully")
                    messagebox.showinfo("Success", "Claim updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update claim.")
            else:
                # Insert new claim
                claim_id = self.db_manager.insert_claim(data)
                self.main_window.set_status(f"New claim created with ID: {claim_id}")
                messagebox.showinfo("Success", f"Claim saved successfully with ID: {claim_id}")
                self.reset_form()
            
            # Refresh search results if available
            if hasattr(self.main_window, 'refresh_search'):
                self.main_window.refresh_search()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save claim: {str(e)}")
    
    def reset_form(self):
        """Clear all form fields"""
        self.current_claim_id = None
        self.entry_date.set_date(datetime.now())
        self.admission_date.set_date("")
        self.customer_name.delete(0, tk.END)
        self.policy_number.delete(0, tk.END)
        self.hospital_name.delete(0, tk.END)
        self.company_name.set("")
        self.claim_number.delete(0, tk.END)
        self.claim_status.set("")
        self.claimed_amount.set_value(None)
        self.approved_amount.set_value(None)
        self.claim_type.set("")
        self.remark.delete("1.0", tk.END)
        self.parent_claim_var.set("")
        
        # Update button text
        self.save_button.config(text="Save Claim")
        
        # Reload parent claims
        self.load_parent_claims()
    
    def load_claim(self, claim_data: Dict):
        """Load claim data for editing"""
        self.current_claim_id = claim_data['id']
        self.set_form_data(claim_data)
        self.save_button.config(text="Update Claim")
    
    def cancel_edit(self):
        """Cancel editing and reset form"""
        if self.current_claim_id:
            if messagebox.askyesno("Cancel Edit", "Are you sure you want to cancel editing? Any unsaved changes will be lost."):
                self.reset_form()
        else:
            self.reset_form()
