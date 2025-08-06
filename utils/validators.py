"""
Validation utilities for insurance claim data
"""

import re
from datetime import datetime
from typing import Dict, List

class ClaimValidator:
    """Validator for insurance claim data"""
    
    def __init__(self):
        # Valid company names
        self.valid_companies = {
            "NIVA", "HDFC", "TATA", "CARE", "NEW INDIA", 
            "NATIONAL", "UNITED", "ORIENTAL", "FUTURE GENERALI"
        }
        
        # Valid claim statuses
        self.valid_statuses = {
            "Intimation", "Submitted", "Approved", "Declined", 
            "Reconsideration", "Settled", "Additional requirement", "Ombudsman"
        }
        
        # Valid claim types
        self.valid_claim_types = {
            "Cashless", "Reimbursement", "Pre-post", "Day care", 
            "Hospital cash", "Health check-up"
        }
    
    def validate_claim(self, claim_data: Dict) -> List[str]:
        """
        Validate claim data and return list of errors
        
        Args:
            claim_data: Dictionary containing claim information
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Required field validation
        required_fields = [
            ('entry_date', 'Entry Date'),
            ('admission_date', 'Date of Admission'),
            ('customer_name', 'Customer Name'),
            ('policy_number', 'Policy Number'),
            ('hospital_name', 'Hospital Name'),
            ('company_name', 'Company Name'),
            ('claim_status', 'Claim Status'),
            ('claim_type', 'Claim Type')
        ]
        
        for field, label in required_fields:
            if not claim_data.get(field) or str(claim_data.get(field)).strip() == '':
                errors.append(f"{label} is required")
        
        # Date validation
        if claim_data.get('entry_date'):
            if not self.validate_date(claim_data['entry_date']):
                errors.append("Entry Date must be in valid date format (YYYY-MM-DD)")
        
        if claim_data.get('admission_date'):
            if not self.validate_date(claim_data['admission_date']):
                errors.append("Date of Admission must be in valid date format (YYYY-MM-DD)")
        
        # Date logic validation
        if claim_data.get('entry_date') and claim_data.get('admission_date'):
            try:
                entry_date = datetime.strptime(claim_data['entry_date'], '%Y-%m-%d')
                admission_date = datetime.strptime(claim_data['admission_date'], '%Y-%m-%d')
                
                # Entry date should not be before admission date (typically)
                # This is a business rule that can be adjusted
                if entry_date < admission_date:
                    errors.append("Entry Date should not be before Date of Admission")
                    
            except ValueError:
                pass  # Date format errors already caught above
        
        # Customer name validation
        if claim_data.get('customer_name'):
            if not self.validate_customer_name(claim_data['customer_name']):
                errors.append("Customer Name should contain only letters, spaces, and common punctuation")
        
        # Policy number validation
        if claim_data.get('policy_number'):
            if not self.validate_policy_number(claim_data['policy_number']):
                errors.append("Policy Number should be alphanumeric and at least 3 characters long")
        
        # Hospital name validation
        if claim_data.get('hospital_name'):
            if len(claim_data['hospital_name'].strip()) < 2:
                errors.append("Hospital Name should be at least 2 characters long")
        
        # Company name validation
        if claim_data.get('company_name'):
            if claim_data['company_name'] not in self.valid_companies:
                errors.append(f"Company Name must be one of: {', '.join(sorted(self.valid_companies))}")
        
        # Claim status validation
        if claim_data.get('claim_status'):
            if claim_data['claim_status'] not in self.valid_statuses:
                errors.append(f"Claim Status must be one of: {', '.join(sorted(self.valid_statuses))}")
        
        # Claim type validation
        if claim_data.get('claim_type'):
            if claim_data['claim_type'] not in self.valid_claim_types:
                errors.append(f"Claim Type must be one of: {', '.join(sorted(self.valid_claim_types))}")
        
        # Amount validation
        if claim_data.get('claimed_amount') is not None:
            if not self.validate_amount(claim_data['claimed_amount']):
                errors.append("Claimed Amount must be a positive number")
        
        if claim_data.get('approved_amount') is not None:
            if not self.validate_amount(claim_data['approved_amount']):
                errors.append("Approved Amount must be a positive number")
        
        # Business logic validation
        if (claim_data.get('claimed_amount') is not None and 
            claim_data.get('approved_amount') is not None):
            if claim_data['approved_amount'] > claim_data['claimed_amount']:
                errors.append("Approved Amount cannot be greater than Claimed Amount")
        
        # Claim number validation for certain statuses
        if claim_data.get('claim_status') in ['Submitted', 'Approved', 'Declined', 'Settled']:
            if not claim_data.get('claim_number') or not claim_data['claim_number'].strip():
                errors.append("Claim Number is required for submitted/processed claims")
        
        # Parent claim validation
        if claim_data.get('parent_claim_id'):
            if claim_data.get('claim_type') not in ['Pre-post', 'Hospital cash']:
                errors.append("Parent claim linking is only allowed for Pre-post and Hospital cash claim types")
        
        return errors
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date string format"""
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_customer_name(self, name: str) -> bool:
        """Validate customer name"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Allow letters, spaces, periods, commas, apostrophes, hyphens
        pattern = r"^[a-zA-Z\s\.\,\'\-]+$"
        return bool(re.match(pattern, name.strip()))
    
    def validate_policy_number(self, policy_number: str) -> bool:
        """Validate policy number"""
        if not policy_number or len(policy_number.strip()) < 3:
            return False
        
        # Allow alphanumeric characters, hyphens, underscores
        pattern = r"^[a-zA-Z0-9\-\_]+$"
        return bool(re.match(pattern, policy_number.strip()))
    
    def validate_amount(self, amount) -> bool:
        """Validate monetary amount"""
        if amount is None:
            return True  # Optional field
        
        try:
            amount_float = float(amount)
            return amount_float >= 0
        except (ValueError, TypeError):
            return False
    
    def validate_search_filters(self, filters: Dict) -> List[str]:
        """Validate search filter values"""
        errors = []
        
        # Date range validation
        date_fields = [
            ('entry_date_from', 'Entry Date From'),
            ('entry_date_to', 'Entry Date To'),
            ('admission_date_from', 'Admission Date From'),
            ('admission_date_to', 'Admission Date To')
        ]
        
        for field, label in date_fields:
            if filters.get(field):
                if not self.validate_date(filters[field]):
                    errors.append(f"{label} must be in valid date format (YYYY-MM-DD)")
        
        # Date range logic validation
        if filters.get('entry_date_from') and filters.get('entry_date_to'):
            try:
                date_from = datetime.strptime(filters['entry_date_from'], '%Y-%m-%d')
                date_to = datetime.strptime(filters['entry_date_to'], '%Y-%m-%d')
                if date_from > date_to:
                    errors.append("Entry Date From cannot be after Entry Date To")
            except ValueError:
                pass
        
        if filters.get('admission_date_from') and filters.get('admission_date_to'):
            try:
                date_from = datetime.strptime(filters['admission_date_from'], '%Y-%m-%d')
                date_to = datetime.strptime(filters['admission_date_to'], '%Y-%m-%d')
                if date_from > date_to:
                    errors.append("Admission Date From cannot be after Admission Date To")
            except ValueError:
                pass
        
        # Dropdown field validation
        if filters.get('company_name') and filters['company_name'] not in self.valid_companies:
            errors.append("Invalid company name in filter")
        
        if filters.get('claim_status') and filters['claim_status'] not in self.valid_statuses:
            errors.append("Invalid claim status in filter")
        
        if filters.get('claim_type') and filters['claim_type'] not in self.valid_claim_types:
            errors.append("Invalid claim type in filter")
        
        return errors
