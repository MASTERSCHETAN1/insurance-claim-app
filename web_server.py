#!/usr/bin/env python3
"""
Web-based Insurance Claim Management System
Flask server to provide web interface for the desktop application
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime
from database import DatabaseManager
from utils.export import ExportManager
import tempfile

app = Flask(__name__)
app.secret_key = 'insurance_claim_management_secret_key'

# Initialize database
db_manager = DatabaseManager()
db_manager.initialize_database()

export_manager = ExportManager()

# Predefined data
COMPANIES = ["NIVA", "HDFC", "TATA", "CARE", "NEW INDIA", "NATIONAL", "UNITED", "ORIENTAL", "FUTURE GENERALI"]
CLAIM_STATUSES = ["Intimation", "Submitted", "Approved", "Declined", "Reconsideration", "Settled", "Additional requirement", "Ombudsman"]
CLAIM_TYPES = ["Cashless", "Reimbursement", "Pre-post", "Day care", "Hospital cash", "Health check-up"]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         companies=COMPANIES, 
                         statuses=CLAIM_STATUSES, 
                         types=CLAIM_TYPES)

@app.route('/api/claims', methods=['GET'])
def get_claims():
    """Get all claims or search claims"""
    filters = {}
    
    # Extract search filters from query parameters
    if request.args.get('customer_name'):
        filters['customer_name'] = request.args.get('customer_name')
    if request.args.get('policy_number'):
        filters['policy_number'] = request.args.get('policy_number')
    if request.args.get('company_name'):
        filters['company_name'] = request.args.get('company_name')
    if request.args.get('claim_status'):
        filters['claim_status'] = request.args.get('claim_status')
    if request.args.get('claim_type'):
        filters['claim_type'] = request.args.get('claim_type')
    if request.args.get('entry_date_from'):
        filters['entry_date_from'] = request.args.get('entry_date_from')
    if request.args.get('entry_date_to'):
        filters['entry_date_to'] = request.args.get('entry_date_to')
    
    try:
        if filters:
            claims = db_manager.search_claims(filters)
        else:
            claims = db_manager.get_all_claims()
        
        return jsonify({
            'success': True,
            'claims': claims,
            'total': len(claims)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/claims/<int:claim_id>', methods=['GET'])
def get_claim(claim_id):
    """Get a specific claim"""
    try:
        claim = db_manager.get_claim_by_id(claim_id)
        if claim:
            return jsonify({
                'success': True,
                'claim': claim
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Claim not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/claims', methods=['POST'])
def create_claim():
    """Create a new claim"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['entry_date', 'admission_date', 'customer_name', 'policy_number', 
                          'hospital_name', 'company_name', 'claim_status', 'claim_type']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Convert amounts to float if provided
        if data.get('claimed_amount'):
            data['claimed_amount'] = float(data['claimed_amount'])
        if data.get('approved_amount'):
            data['approved_amount'] = float(data['approved_amount'])
        
        claim_id = db_manager.insert_claim(data)
        
        return jsonify({
            'success': True,
            'claim_id': claim_id,
            'message': 'Claim created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/claims/<int:claim_id>', methods=['PUT'])
def update_claim(claim_id):
    """Update an existing claim"""
    try:
        data = request.json
        
        # Convert amounts to float if provided
        if data.get('claimed_amount'):
            data['claimed_amount'] = float(data['claimed_amount'])
        if data.get('approved_amount'):
            data['approved_amount'] = float(data['approved_amount'])
        
        success = db_manager.update_claim(claim_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Claim updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Claim not found or update failed'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/claims/<int:claim_id>', methods=['DELETE'])
def delete_claim(claim_id):
    """Delete a claim"""
    try:
        success = db_manager.delete_claim(claim_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Claim deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Claim not found or delete failed'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/claims/<int:claim_id>/linked', methods=['GET'])
def get_linked_claims(claim_id):
    """Get claims linked to a parent claim"""
    try:
        linked_claims = db_manager.get_linked_claims(claim_id)
        return jsonify({
            'success': True,
            'linked_claims': linked_claims
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/main-claims', methods=['GET'])
def get_main_claims():
    """Get main claims that can be used as parent claims, with optional filtering"""
    try:
        # Get filter parameters
        customer_name = request.args.get('customer_name', '').strip()
        policy_number = request.args.get('policy_number', '').strip()
        admission_date_from = request.args.get('admission_date_from', '').strip()
        admission_date_to = request.args.get('admission_date_to', '').strip()
        
        if customer_name or policy_number or admission_date_from or admission_date_to:
            # Use filtered search for main claims
            filters = {}
            if customer_name:
                filters['customer_name'] = customer_name
            if policy_number:
                filters['policy_number'] = policy_number
            if admission_date_from:
                filters['admission_date_from'] = admission_date_from
            if admission_date_to:
                filters['admission_date_to'] = admission_date_to
            
            main_claims = db_manager.get_filtered_main_claims(filters)
        else:
            # Get all main claims
            main_claims = db_manager.get_main_claims()
            
        return jsonify({
            'success': True,
            'main_claims': main_claims
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get claim statistics"""
    try:
        stats = db_manager.get_claim_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export claims to CSV"""
    try:
        filters = request.json or {}
        
        if filters:
            claims = db_manager.search_claims(filters)
        else:
            claims = db_manager.get_all_claims()
        
        if not claims:
            return jsonify({
                'success': False,
                'error': 'No claims to export'
            }), 400
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        filename = temp_file.name
        temp_file.close()
        
        # Export to CSV
        success = export_manager.export_to_csv(claims, filename)
        
        if success:
            return send_file(filename, 
                           as_attachment=True, 
                           download_name=f'insurance_claims_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                           mimetype='text/csv')
        else:
            return jsonify({
                'success': False,
                'error': 'Export failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # Clean up temp file
        if 'filename' in locals() and os.path.exists(filename):
            os.unlink(filename)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)