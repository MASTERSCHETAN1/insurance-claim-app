// Insurance Claim Management System - JavaScript
let currentEditingId = null;
let allClaims = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default for entry date
    document.getElementById('entryDate').value = new Date().toISOString().split('T')[0];
    
    // Load all claims on page load
    loadAllClaims();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load main claims for linking
    loadMainClaims();
});

function setupEventListeners() {
    // Claim form submission
    document.getElementById('claimForm').addEventListener('submit', handleClaimSubmission);
    
    // Search form submission
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    
    // Claim type change for parent claim linking
    document.getElementById('claimType').addEventListener('change', handleClaimTypeChange);
    
    // Update parent claim list when customer details change
    document.getElementById('customerName').addEventListener('input', updateParentClaimList);
    document.getElementById('policyNumber').addEventListener('input', updateParentClaimList);
    document.getElementById('admissionDate').addEventListener('change', updateParentClaimList);
    
    // Tab switching
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            if (e.target.id === 'stats-tab') {
                loadStatistics();
            }
        });
    });
}

async function handleClaimSubmission(e) {
    e.preventDefault();
    
    const formData = getFormData();
    
    try {
        let response;
        if (currentEditingId) {
            response = await fetch(`/api/claims/${currentEditingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        } else {
            response = await fetch('/api/claims', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', result.message || (currentEditingId ? 'Claim updated successfully!' : 'Claim created successfully!'));
            clearForm();
            loadAllClaims(); // Refresh the claims list
        } else {
            showAlert('danger', result.error || 'An error occurred while saving the claim');
        }
    } catch (error) {
        showAlert('danger', 'Network error: ' + error.message);
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    const searchParams = {
        customer_name: document.getElementById('searchCustomer').value,
        policy_number: document.getElementById('searchPolicy').value,
        company_name: document.getElementById('searchCompany').value,
        claim_status: document.getElementById('searchStatus').value,
        claim_type: document.getElementById('searchType').value,
        entry_date_from: document.getElementById('searchDateFrom').value,
        entry_date_to: document.getElementById('searchDateTo').value
    };
    
    // Remove empty parameters
    Object.keys(searchParams).forEach(key => {
        if (!searchParams[key]) {
            delete searchParams[key];
        }
    });
    
    try {
        const queryString = new URLSearchParams(searchParams).toString();
        const response = await fetch(`/api/claims?${queryString}`);
        const result = await response.json();
        
        if (result.success) {
            allClaims = result.claims;
            displayClaims(result.claims);
            updateResultsCount(result.claims.length, Object.keys(searchParams).length > 0);
        } else {
            showAlert('danger', result.error || 'Search failed');
        }
    } catch (error) {
        showAlert('danger', 'Search error: ' + error.message);
    }
}

function handleClaimTypeChange() {
    const claimType = document.getElementById('claimType').value;
    const parentClaimSelect = document.getElementById('parentClaim');
    
    if (claimType === 'Pre-post' || claimType === 'Hospital cash') {
        parentClaimSelect.disabled = false;
        loadFilteredMainClaims(); // Load filtered claims based on current form data
    } else {
        parentClaimSelect.disabled = true;
        parentClaimSelect.value = '';
        // Reset to show all main claims
        loadMainClaims();
    }
}

function getFormData() {
    return {
        entry_date: document.getElementById('entryDate').value,
        admission_date: document.getElementById('admissionDate').value,
        customer_name: document.getElementById('customerName').value,
        policy_number: document.getElementById('policyNumber').value,
        hospital_name: document.getElementById('hospitalName').value,
        company_name: document.getElementById('companyName').value,
        claim_number: document.getElementById('claimNumber').value || null,
        claim_status: document.getElementById('claimStatus').value,
        claimed_amount: document.getElementById('claimedAmount').value || null,
        approved_amount: document.getElementById('approvedAmount').value || null,
        claim_type: document.getElementById('claimType').value,
        parent_claim_id: document.getElementById('parentClaim').value || null,
        remark: document.getElementById('remark').value,
        tpa_name: document.getElementById('tpaName').value || null
    };
}

function clearForm() {
    document.getElementById('claimForm').reset();
    document.getElementById('entryDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('claimId').value = '';
    document.getElementById('parentClaim').disabled = true;
    document.getElementById('form-title').innerHTML = '<i class="fas fa-file-plus me-2"></i>New Claim Entry';
    document.getElementById('cancelBtn').style.display = 'none';
    currentEditingId = null;
}

function clearSearch() {
    document.getElementById('searchForm').reset();
}

async function loadAllClaims() {
    try {
        const response = await fetch('/api/claims');
        const result = await response.json();
        
        if (result.success) {
            allClaims = result.claims;
            displayClaims(result.claims);
            updateResultsCount(result.claims.length, false);
        } else {
            showAlert('danger', result.error || 'Failed to load claims');
        }
    } catch (error) {
        showAlert('danger', 'Error loading claims: ' + error.message);
    }
}

async function loadMainClaims() {
    try {
        const response = await fetch('/api/main-claims');
        const result = await response.json();
        
        if (result.success) {
            populateParentClaimSelect(result.main_claims);
        }
    } catch (error) {
        console.error('Error loading main claims:', error);
    }
}

async function loadFilteredMainClaims() {
    const customerName = document.getElementById('customerName').value.trim();
    const policyNumber = document.getElementById('policyNumber').value.trim();
    const admissionDate = document.getElementById('admissionDate').value;
    
    // Only filter if we have customer name and policy number
    if (!customerName || !policyNumber) {
        loadMainClaims(); // Load all main claims if no filters
        return;
    }
    
    try {
        const filters = {
            customer_name: customerName,
            policy_number: policyNumber
        };
        
        if (admissionDate) {
            filters.admission_date_from = admissionDate;
            filters.admission_date_to = admissionDate;
        }
        
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/main-claims?${queryString}`);
        const result = await response.json();
        
        if (result.success) {
            populateParentClaimSelect(result.main_claims);
        }
    } catch (error) {
        console.error('Error loading filtered main claims:', error);
        loadMainClaims(); // Fallback to all claims
    }
}

function populateParentClaimSelect(claims) {
    const parentSelect = document.getElementById('parentClaim');
    // Clear existing options except the first one
    parentSelect.innerHTML = '<option value="">Select Main Claim</option>';
    
    if (claims.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No matching main claims found';
        option.disabled = true;
        parentSelect.appendChild(option);
        return;
    }
    
    claims.forEach(claim => {
        const option = document.createElement('option');
        option.value = claim.id;
        option.textContent = `${claim.id} - ${claim.customer_name} (${claim.policy_number})`;
        if (claim.claim_number) {
            option.textContent += ` - ${claim.claim_number}`;
        }
        option.textContent += ` - ${formatDate(claim.admission_date)}`;
        parentSelect.appendChild(option);
    });
}

function updateParentClaimList() {
    const claimType = document.getElementById('claimType').value;
    
    // Only update if claim type is Pre-post or Hospital cash
    if (claimType === 'Pre-post' || claimType === 'Hospital cash') {
        loadFilteredMainClaims();
    }
}

function displayClaims(claims) {
    const tbody = document.getElementById('claimsTableBody');
    tbody.innerHTML = '';
    
    if (claims.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center">No claims found</td></tr>';
        return;
    }
    
    claims.forEach(claim => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${claim.id}</td>
            <td>${formatDate(claim.entry_date)}</td>
            <td>${claim.customer_name}</td>
            <td>${claim.policy_number}</td>
            <td>${claim.hospital_name}</td>
            <td>${claim.company_name}</td>
            <td>${claim.claim_number || '-'}</td>
            <td><span class="badge ${getStatusBadgeClass(claim.claim_status)} status-badge">${claim.claim_status}</span></td>
            <td>${claim.claim_type}</td>
            <td>${claim.claimed_amount ? '₹' + formatCurrency(claim.claimed_amount) : '-'}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary btn-sm" onclick="editClaim(${claim.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-info btn-sm" onclick="viewLinkedClaims(${claim.id})" title="View Linked">
                        <i class="fas fa-link"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteClaim(${claim.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function getStatusBadgeClass(status) {
    const statusClasses = {
        'Approved': 'bg-success',
        'Settled': 'bg-primary',
        'Declined': 'bg-danger',
        'Submitted': 'bg-info',
        'Intimation': 'bg-warning',
        'Reconsideration': 'bg-secondary',
        'Additional requirement': 'bg-dark',
        'Ombudsman': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN').format(amount);
}

function updateResultsCount(count, isFiltered) {
    const badge = document.getElementById('resultsCount');
    const text = isFiltered ? `${count} claim(s) found` : `${count} claim(s)`;
    badge.textContent = text;
}

async function editClaim(claimId) {
    try {
        const response = await fetch(`/api/claims/${claimId}`);
        const result = await response.json();
        
        if (result.success) {
            const claim = result.claim;
            
            // Populate form fields
            document.getElementById('claimId').value = claim.id;
            document.getElementById('entryDate').value = claim.entry_date;
            document.getElementById('admissionDate').value = claim.admission_date;
            document.getElementById('customerName').value = claim.customer_name;
            document.getElementById('policyNumber').value = claim.policy_number;
            document.getElementById('hospitalName').value = claim.hospital_name;
            document.getElementById('companyName').value = claim.company_name;
            document.getElementById('claimNumber').value = claim.claim_number || '';
            document.getElementById('claimStatus').value = claim.claim_status;
            document.getElementById('claimedAmount').value = claim.claimed_amount || '';
            document.getElementById('approvedAmount').value = claim.approved_amount || '';
            document.getElementById('claimType').value = claim.claim_type;
            document.getElementById('remark').value = claim.remark || '';
            document.getElementById('tpaName').value = claim.tpa_name || '';
            
            // Handle parent claim
            if (claim.parent_claim_id) {
                document.getElementById('parentClaim').value = claim.parent_claim_id;
            }
            
            // Update UI for editing mode
            currentEditingId = claimId;
            document.getElementById('form-title').innerHTML = '<i class="fas fa-edit me-2"></i>Edit Claim';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            
            // Switch to form tab
            const formTab = new bootstrap.Tab(document.getElementById('claim-form-tab'));
            formTab.show();
            
            // Handle claim type change
            handleClaimTypeChange();
            
        } else {
            showAlert('danger', result.error || 'Failed to load claim for editing');
        }
    } catch (error) {
        showAlert('danger', 'Error loading claim: ' + error.message);
    }
}

async function deleteClaim(claimId) {
    if (!confirm('Are you sure you want to delete this claim? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/claims/${claimId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', 'Claim deleted successfully');
            loadAllClaims(); // Refresh the list
        } else {
            showAlert('danger', result.error || 'Failed to delete claim');
        }
    } catch (error) {
        showAlert('danger', 'Error deleting claim: ' + error.message);
    }
}

async function viewLinkedClaims(claimId) {
    try {
        const response = await fetch(`/api/claims/${claimId}/linked`);
        const result = await response.json();
        
        if (result.success) {
            if (result.linked_claims.length === 0) {
                showAlert('info', 'No linked claims found for this claim.');
            } else {
                // Create and show modal with linked claims
                showLinkedClaimsModal(result.linked_claims);
            }
        } else {
            showAlert('danger', result.error || 'Failed to load linked claims');
        }
    } catch (error) {
        showAlert('danger', 'Error loading linked claims: ' + error.message);
    }
}

function showLinkedClaimsModal(linkedClaims) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Linked Claims</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Customer</th>
                                    <th>Policy</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${linkedClaims.map(claim => `
                                    <tr>
                                        <td>${claim.id}</td>
                                        <td>${claim.customer_name}</td>
                                        <td>${claim.policy_number}</td>
                                        <td>${claim.claim_type}</td>
                                        <td><span class="badge ${getStatusBadgeClass(claim.claim_status)} status-badge">${claim.claim_status}</span></td>
                                        <td>${claim.claimed_amount ? '₹' + formatCurrency(claim.claimed_amount) : '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const result = await response.json();
        
        if (result.success) {
            displayStatistics(result.statistics);
        } else {
            showAlert('danger', result.error || 'Failed to load statistics');
        }
    } catch (error) {
        showAlert('danger', 'Error loading statistics: ' + error.message);
    }
}

function displayStatistics(stats) {
    const content = document.getElementById('statisticsContent');
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5 class="card-title">Total Claims</h5>
                        <h2 class="mb-0">${stats.total_claims}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5 class="card-title">Total Claimed</h5>
                        <h2 class="mb-0">₹${formatCurrency(stats.total_claimed)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5 class="card-title">Total Approved</h5>
                        <h2 class="mb-0">₹${formatCurrency(stats.total_approved)}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Claims by Status</h6>
                    </div>
                    <div class="card-body">
                        ${Object.entries(stats.by_status || {}).map(([status, count]) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge ${getStatusBadgeClass(status)} status-badge">${status}</span>
                                <strong>${count}</strong>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Claims by Company</h6>
                    </div>
                    <div class="card-body">
                        ${Object.entries(stats.by_company || {}).map(([company, count]) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${company}</span>
                                <strong>${count}</strong>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function exportClaims() {
    try {
        // Get current search filters
        const searchParams = {
            customer_name: document.getElementById('searchCustomer').value,
            policy_number: document.getElementById('searchPolicy').value,
            company_name: document.getElementById('searchCompany').value,
            claim_status: document.getElementById('searchStatus').value,
            claim_type: document.getElementById('searchType').value,
            entry_date_from: document.getElementById('searchDateFrom').value,
            entry_date_to: document.getElementById('searchDateTo').value
        };
        
        // Remove empty parameters
        Object.keys(searchParams).forEach(key => {
            if (!searchParams[key]) {
                delete searchParams[key];
            }
        });
        
        const response = await fetch('/api/export/csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchParams)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `insurance_claims_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('success', 'Claims exported successfully');
        } else {
            const result = await response.json();
            showAlert('danger', result.error || 'Export failed');
        }
    } catch (error) {
        showAlert('danger', 'Export error: ' + error.message);
    }
}

function cancelEdit() {
    if (confirm('Are you sure you want to cancel editing? Any unsaved changes will be lost.')) {
        clearForm();
    }
}

function showAlert(type, message) {
    // Remove any existing alerts
    const existingAlert = document.querySelector('.alert-dismissible');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert && alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}