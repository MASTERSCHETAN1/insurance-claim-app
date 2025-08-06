"""
Claim data model for Insurance Claim Management System
"""

from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field

@dataclass
class Claim:
    """Data model for insurance claim"""
    
    # Required fields
    entry_date: str
    admission_date: str
    customer_name: str
    policy_number: str
    hospital_name: str
    company_name: str
    claim_status: str
    claim_type: str
    
    # Optional fields
    id: Optional[int] = None
    claim_number: Optional[str] = None
    claimed_amount: Optional[float] = None
    approved_amount: Optional[float] = None
    remark: Optional[str] = None
    parent_claim_id: Optional[int] = None
    tpa_name: Optional[str] = None
    
    # System fields
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Linked claims (not stored in DB, populated when needed)
    linked_claims: List['Claim'] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Claim':
        """Create Claim instance from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict:
        """Convert Claim instance to dictionary"""
        return {
            'id': self.id,
            'entry_date': self.entry_date,
            'admission_date': self.admission_date,
            'customer_name': self.customer_name,
            'policy_number': self.policy_number,
            'hospital_name': self.hospital_name,
            'company_name': self.company_name,
            'claim_number': self.claim_number,
            'claim_status': self.claim_status,
            'claimed_amount': self.claimed_amount,
            'approved_amount': self.approved_amount,
            'claim_type': self.claim_type,
            'remark': self.remark,
            'parent_claim_id': self.parent_claim_id,
            'tpa_name': self.tpa_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def is_main_claim(self) -> bool:
        """Check if this is a main claim (can have linked claims)"""
        return self.claim_type in ['Cashless', 'Reimbursement']
    
    def can_be_linked(self) -> bool:
        """Check if this claim can be linked to a parent claim"""
        return self.claim_type in ['Pre-post', 'Hospital cash']
    
    def get_display_name(self) -> str:
        """Get a display name for this claim"""
        display = f"{self.customer_name} ({self.policy_number})"
        if self.claim_number:
            display += f" - {self.claim_number}"
        return display
    
    def get_financial_summary(self) -> Dict[str, float]:
        """Get financial summary of the claim"""
        return {
            'claimed_amount': self.claimed_amount or 0.0,
            'approved_amount': self.approved_amount or 0.0,
            'pending_amount': (self.claimed_amount or 0.0) - (self.approved_amount or 0.0)
        }
    
    def is_settled(self) -> bool:
        """Check if the claim is settled"""
        return self.claim_status == 'Settled'
    
    def is_approved(self) -> bool:
        """Check if the claim is approved"""
        return self.claim_status == 'Approved'
    
    def is_declined(self) -> bool:
        """Check if the claim is declined"""
        return self.claim_status == 'Declined'
    
    def needs_follow_up(self) -> bool:
        """Check if the claim needs follow-up"""
        return self.claim_status in ['Additional requirement', 'Reconsideration']
    
    def validate(self) -> List[str]:
        """Validate claim data and return list of errors"""
        from utils.validators import ClaimValidator
        
        validator = ClaimValidator()
        return validator.validate_claim(self.to_dict())
    
    def __str__(self) -> str:
        """String representation of the claim"""
        return f"Claim({self.id}): {self.customer_name} - {self.claim_type} - {self.claim_status}"
    
    def __repr__(self) -> str:
        """Developer representation of the claim"""
        return (f"Claim(id={self.id}, customer_name='{self.customer_name}', "
               f"policy_number='{self.policy_number}', claim_type='{self.claim_type}', "
               f"status='{self.claim_status}')")

class ClaimStatus:
    """Constants for claim statuses"""
    INTIMATION = "Intimation"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    DECLINED = "Declined"
    RECONSIDERATION = "Reconsideration"
    SETTLED = "Settled"
    ADDITIONAL_REQUIREMENT = "Additional requirement"
    OMBUDSMAN = "Ombudsman"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """Get all status values"""
        return [
            cls.INTIMATION, cls.SUBMITTED, cls.APPROVED, cls.DECLINED,
            cls.RECONSIDERATION, cls.SETTLED, cls.ADDITIONAL_REQUIREMENT, cls.OMBUDSMAN
        ]
    
    @classmethod
    def get_active_statuses(cls) -> List[str]:
        """Get statuses that indicate active claims"""
        return [cls.INTIMATION, cls.SUBMITTED, cls.ADDITIONAL_REQUIREMENT, cls.RECONSIDERATION]
    
    @classmethod
    def get_final_statuses(cls) -> List[str]:
        """Get statuses that indicate claim is finalized"""
        return [cls.APPROVED, cls.DECLINED, cls.SETTLED, cls.OMBUDSMAN]

class ClaimType:
    """Constants for claim types"""
    CASHLESS = "Cashless"
    REIMBURSEMENT = "Reimbursement"
    PRE_POST = "Pre-post"
    DAY_CARE = "Day care"
    HOSPITAL_CASH = "Hospital cash"
    HEALTH_CHECKUP = "Health check-up"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """Get all claim type values"""
        return [
            cls.CASHLESS, cls.REIMBURSEMENT, cls.PRE_POST,
            cls.DAY_CARE, cls.HOSPITAL_CASH, cls.HEALTH_CHECKUP
        ]
    
    @classmethod
    def get_main_types(cls) -> List[str]:
        """Get main claim types that can have linked claims"""
        return [cls.CASHLESS, cls.REIMBURSEMENT]
    
    @classmethod
    def get_linkable_types(cls) -> List[str]:
        """Get claim types that can be linked to main claims"""
        return [cls.PRE_POST, cls.HOSPITAL_CASH]

class Company:
    """Constants for insurance companies"""
    NIVA = "NIVA"
    HDFC = "HDFC"
    TATA = "TATA"
    CARE = "CARE"
    NEW_INDIA = "NEW INDIA"
    NATIONAL = "NATIONAL"
    UNITED = "UNITED"
    ORIENTAL = "ORIENTAL"
    FUTURE_GENERALI = "FUTURE GENERALI"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """Get all company values"""
        return [
            cls.NIVA, cls.HDFC, cls.TATA, cls.CARE, cls.NEW_INDIA,
            cls.NATIONAL, cls.UNITED, cls.ORIENTAL, cls.FUTURE_GENERALI
        ]
