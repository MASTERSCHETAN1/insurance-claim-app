"""
Database manager for Insurance Claim Management System
Handles SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "insurance_claims.db"):
        """Initialize database manager with SQLite database"""
        self.db_path = db_path
        
    def get_connection(self):
        """Get a new database connection for thread safety"""
        # Always create a new connection to avoid threading issues
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        # Enable foreign key constraints
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create claims table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_date TEXT NOT NULL,
                    admission_date TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    policy_number TEXT NOT NULL,
                    hospital_name TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    claim_number TEXT,
                    claim_status TEXT NOT NULL,
                    claimed_amount REAL,
                    approved_amount REAL,
                    claim_type TEXT NOT NULL,
                    remark TEXT,
                    parent_claim_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_claim_id) REFERENCES claims (id)
                )
            ''')
            
            # Create indexes for better search performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_name ON claims (customer_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_policy_number ON claims (policy_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_claim_status ON claims (claim_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_name ON claims (company_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entry_date ON claims (entry_date)')
            
            # Check if tpa_name column exists, add if not
            cursor.execute("PRAGMA table_info(claims)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'tpa_name' not in columns:
                cursor.execute('ALTER TABLE claims ADD COLUMN tpa_name TEXT')
            
            conn.commit()
        finally:
            conn.close()
    
    def insert_claim(self, claim_data: Dict) -> int:
        """Insert a new claim and return the claim ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Add timestamp
            claim_data['created_at'] = datetime.now().isoformat()
            claim_data['updated_at'] = datetime.now().isoformat()
            
            columns = ', '.join(claim_data.keys())
            placeholders = ', '.join(['?' for _ in claim_data])
            values = list(claim_data.values())
            
            query = f"INSERT INTO claims ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.lastrowid or 0
        finally:
            conn.close()
    
    def update_claim(self, claim_id: int, claim_data: Dict) -> bool:
        """Update an existing claim"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Add updated timestamp
            claim_data['updated_at'] = datetime.now().isoformat()
            
            # Build SET clause
            set_clause = ', '.join([f"{key} = ?" for key in claim_data.keys()])
            values = list(claim_data.values()) + [claim_id]
            
            query = f"UPDATE claims SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_claim_by_id(self, claim_id: int) -> Optional[Dict]:
        """Get a single claim by ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
        finally:
            conn.close()
    
    def search_claims(self, filters: Dict) -> List[Dict]:
        """Search claims with various filters"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build WHERE clause dynamically
            where_conditions = []
            values = []
            
            if filters.get('customer_name'):
                where_conditions.append("customer_name LIKE ?")
                values.append(f"%{filters['customer_name']}%")
            
            if filters.get('policy_number'):
                where_conditions.append("policy_number LIKE ?")
                values.append(f"%{filters['policy_number']}%")
            
            if filters.get('claim_status'):
                where_conditions.append("claim_status = ?")
                values.append(filters['claim_status'])
            
            if filters.get('claim_type'):
                where_conditions.append("claim_type = ?")
                values.append(filters['claim_type'])
            
            if filters.get('company_name'):
                where_conditions.append("company_name = ?")
                values.append(filters['company_name'])
            
            if filters.get('entry_date_from'):
                where_conditions.append("entry_date >= ?")
                values.append(filters['entry_date_from'])
            
            if filters.get('entry_date_to'):
                where_conditions.append("entry_date <= ?")
                values.append(filters['entry_date_to'])
            
            if filters.get('admission_date_from'):
                where_conditions.append("admission_date >= ?")
                values.append(filters['admission_date_from'])
            
            if filters.get('admission_date_to'):
                where_conditions.append("admission_date <= ?")
                values.append(filters['admission_date_to'])
            
            # Build complete query
            query = "SELECT * FROM claims"
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            query += " ORDER BY entry_date DESC, id DESC"
            
            cursor.execute(query, values)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_all_claims(self) -> List[Dict]:
        """Get all claims ordered by entry date"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM claims ORDER BY entry_date DESC, id DESC")
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_linked_claims(self, parent_claim_id: int) -> List[Dict]:
        """Get all claims linked to a parent claim"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM claims WHERE parent_claim_id = ?", (parent_claim_id,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_main_claims(self) -> List[Dict]:
        """Get claims that can be used as parent claims (Cashless or Reimbursement)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, customer_name, policy_number, claim_number, claim_type, entry_date, admission_date
                FROM claims 
                WHERE claim_type IN ('Cashless', 'Reimbursement')
                ORDER BY entry_date DESC
            """)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_filtered_main_claims(self, filters: Dict) -> List[Dict]:
        """Get filtered main claims that can be used as parent claims"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build WHERE clause for main claims with filters
            where_conditions = ["claim_type IN ('Cashless', 'Reimbursement')"]
            values = []
            
            if filters.get('customer_name'):
                where_conditions.append("customer_name LIKE ?")
                values.append(f"%{filters['customer_name']}%")
            
            if filters.get('policy_number'):
                where_conditions.append("policy_number LIKE ?")
                values.append(f"%{filters['policy_number']}%")
            
            if filters.get('admission_date_from'):
                where_conditions.append("admission_date >= ?")
                values.append(filters['admission_date_from'])
            
            if filters.get('admission_date_to'):
                where_conditions.append("admission_date <= ?")
                values.append(filters['admission_date_to'])
            
            query = f"""
                SELECT id, customer_name, policy_number, claim_number, claim_type, entry_date, admission_date
                FROM claims 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY entry_date DESC
            """
            
            cursor.execute(query, values)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def delete_claim(self, claim_id: int) -> bool:
        """Delete a claim (with cascade for linked claims)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # First delete linked claims
            cursor.execute("DELETE FROM claims WHERE parent_claim_id = ?", (claim_id,))
            # Then delete the main claim
            cursor.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_claim_statistics(self) -> Dict:
        """Get basic statistics about claims"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total claims
            cursor.execute("SELECT COUNT(*) FROM claims")
            stats['total_claims'] = cursor.fetchone()[0]
            
            # Claims by status
            cursor.execute("SELECT claim_status, COUNT(*) FROM claims GROUP BY claim_status")
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Claims by company
            cursor.execute("SELECT company_name, COUNT(*) FROM claims GROUP BY company_name")
            stats['by_company'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total claimed amount
            cursor.execute("SELECT SUM(claimed_amount) FROM claims WHERE claimed_amount IS NOT NULL")
            result = cursor.fetchone()[0]
            stats['total_claimed'] = result if result else 0
            
            # Total approved amount
            cursor.execute("SELECT SUM(approved_amount) FROM claims WHERE approved_amount IS NOT NULL")
            result = cursor.fetchone()[0]
            stats['total_approved'] = result if result else 0
            
            return stats
        finally:
            conn.close()
    
    def close(self):
        """Close database connection - no longer needed with per-request connections"""
        pass
