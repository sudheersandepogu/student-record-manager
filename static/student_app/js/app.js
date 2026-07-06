// Global variables
let studentIdToDelete = null;
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

// DOM Elements
const studentForm = document.getElementById('student-form');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const ageInput = document.getElementById('age');
const gradeSelect = document.getElementById('grade');
const btnClear = document.getElementById('btn-clear');
const searchInput = document.getElementById('search-input');
const searchCountBadge = document.getElementById('search-count');
const studentTableBody = document.getElementById('student-table-body');
const toastContainer = document.getElementById('toast-container');

// Confirm Modal elements
const confirmModal = document.getElementById('confirm-modal');
const deleteStudentNameSpan = document.getElementById('delete-student-name');
const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
const cancelDeleteBtn = document.getElementById('cancel-delete-btn');

// Stats Elements
const statTotalStudents = document.getElementById('stat-total-students');
const statAverageAge = document.getElementById('stat-average-age');
const statHighestGrade = document.getElementById('stat-highest-grade');
const statTotalRecords = document.getElementById('stat-total-records');

// CSRF Token
const getCsrfToken = () => {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Render initial icons
    lucide.createIcons();
    
    // Fetch initial students list and statistics
    fetchStudents();
    
    // Setup listeners
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Form Submit
    studentForm.addEventListener('submit', handleFormSubmit);
    
    // Clear Form
    btnClear.addEventListener('click', clearForm);
    
    // Live Search
    searchInput.addEventListener('input', handleSearchInput);
    
    // Modal Actions
    cancelDeleteBtn.addEventListener('click', hideDeleteModal);
    confirmDeleteBtn.addEventListener('click', executeDeleteStudent);
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) hideDeleteModal();
    });
}

// Fetch Students & Stats
async function fetchStudents() {
    try {
        const response = await fetch('/api/students/');
        const data = await response.json();
        
        if (data.success) {
            updateTable(data.students);
            updateDashboard(data.stats);
        } else {
            showToast(data.error || 'Failed to load records.', 'error');
        }
    } catch (error) {
        console.error('Error fetching students:', error);
        showToast('Connection error. Failed to load students.', 'error');
    }
}

// Update Dashboard Statistics
function updateDashboard(stats) {
    if (!stats) return;
    
    statTotalStudents.textContent = stats.total_students;
    statAverageAge.textContent = stats.average_age.toFixed(1);
    
    if (stats.highest_grade_name && stats.highest_grade_name !== 'N/A') {
        statHighestGrade.textContent = `${stats.highest_grade_name} (${stats.highest_grade_count})`;
    } else {
        statHighestGrade.textContent = 'N/A';
    }
    
    statTotalRecords.textContent = stats.total_records;
}

// Update Table Rows
function updateTable(students) {
    studentTableBody.innerHTML = '';
    
    if (!students || students.length === 0) {
        studentTableBody.innerHTML = `
            <tr class="table-empty-row">
                <td colspan="7" class="empty-state">
                    <div class="empty-icon-container">
                        <i data-lucide="folder-open"></i>
                    </div>
                    <div>No student records found. Add one on the left!</div>
                </td>
            </tr>
        `;
        lucide.createIcons();
        return;
    }
    
    students.forEach((student, index) => {
        const row = document.createElement('tr');
        row.className = 'table-row-animate';
        row.style.animationDelay = `${index * 0.05}s`;
        
        // Format Grade Badge Class
        let gradeClass = 'grade-badge';
        if (student.grade === 'A+' || student.grade === 'A') gradeClass += ' grade-A';
        else if (student.grade === 'B') gradeClass += ' grade-B';
        else if (student.grade === 'C') gradeClass += ' grade-C';
        else gradeClass += ' grade-D';
        
        row.innerHTML = `
            <td>#${student.id}</td>
            <td style="font-weight: 600;">${escapeHTML(student.name)}</td>
            <td>${escapeHTML(student.email)}</td>
            <td>${student.age}</td>
            <td><span class="${gradeClass}">${student.grade}</span></td>
            <td>${student.created_at}</td>
            <td>
                <button class="btn-action-delete" title="Delete Student" onclick="confirmDeleteStudent(${student.id}, '${escapeHTML(student.name.replace(/'/g, "\\'"))}')">
                    <i data-lucide="trash-2" style="width: 1.1rem; height: 1.1rem;"></i>
                </button>
            </td>
        `;
        
        studentTableBody.appendChild(row);
    });
    
    // Bind lucide icons to newly appended elements
    lucide.createIcons();
}

// Handle Form Submission with Validation
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Clear previous errors
    clearErrors();
    
    // Get fields values
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const ageVal = ageInput.value.trim();
    const grade = gradeSelect.value;
    
    let isValid = true;
    
    // Validation: Name
    if (!name) {
        showFieldError('name', 'Student name is required.');
        isValid = false;
    } else if (name.length < 2) {
        showFieldError('name', 'Name must be at least 2 characters long.');
        isValid = false;
    }
    
    // Validation: Email
    if (!email) {
        showFieldError('email', 'Email address is required.');
        isValid = false;
    } else if (!EMAIL_REGEX.test(email)) {
        showFieldError('email', 'Please enter a valid email address (e.g. name@domain.com).');
        isValid = false;
    }
    
    // Validation: Age
    if (!ageVal) {
        showFieldError('age', 'Age is required.');
        isValid = false;
    } else {
        const age = parseInt(ageVal, 10);
        if (isNaN(age) || age <= 0 || age > 120) {
            showFieldError('age', 'Please enter a valid age between 1 and 120.');
            isValid = false;
        }
    }
    
    // Validation: Grade
    if (!grade) {
        showFieldError('grade', 'Please select a student grade.');
        isValid = false;
    }
    
    if (!isValid) return;
    
    // Disable submit button
    const btnSubmit = document.getElementById('btn-submit');
    const originalText = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span class="spinner" style="width: 1rem; height: 1rem; border-width: 2px;"></span> Saving...`;
    
    try {
        const response = await fetch('/api/add-student/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                name,
                email,
                age: parseInt(ageVal, 10),
                grade
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message || 'Student added successfully!', 'success');
            clearForm();
            fetchStudents(); // Reloads table & dashboard statistics
        } else {
            showToast(data.error || 'Failed to save student.', 'error');
            // If error is duplicate email, highlight email field
            if (data.error && data.error.toLowerCase().includes('email')) {
                showFieldError('email', data.error);
            }
        }
    } catch (error) {
        console.error('Submit Error:', error);
        showToast('Connection error. Failed to save student.', 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    }
}

// Live Search Input handler (instant update)
let searchTimeout;
function handleSearchInput() {
    clearTimeout(searchTimeout);
    
    // Fetch query
    const query = searchInput.value.trim();
    
    // Debounce search requests slightly (200ms) to reduce db query spikes
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search-student/?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                updateTable(data.students);
                
                // Show badge with search results count
                if (query) {
                    searchCountBadge.style.display = 'inline-block';
                    searchCountBadge.textContent = `${data.students.length} found`;
                } else {
                    searchCountBadge.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 200);
}

// Open Delete Confirmation Dialog
window.confirmDeleteStudent = function(id, name) {
    studentIdToDelete = id;
    deleteStudentNameSpan.textContent = name;
    confirmModal.classList.add('active');
};

function hideDeleteModal() {
    confirmModal.classList.remove('active');
    studentIdToDelete = null;
}

// Execute Delete API
async function executeDeleteStudent() {
    if (!studentIdToDelete) return;
    
    hideDeleteModal();
    
    try {
        const response = await fetch(`/api/delete-student/${studentIdToDelete}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message || 'Record deleted successfully.', 'success');
            // Auto refresh list & dashboard statistics
            fetchStudents();
            // Clear search field if search was active
            if (searchInput.value) {
                searchInput.value = '';
                searchCountBadge.style.display = 'none';
            }
        } else {
            showToast(data.error || 'Failed to delete record.', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Connection error. Failed to delete record.', 'error');
    }
}

// Validation Utilities
function showFieldError(fieldId, message) {
    const errorSpan = document.getElementById(`error-${fieldId}`);
    if (errorSpan) {
        errorSpan.textContent = message;
        errorSpan.style.opacity = '1';
    }
    
    const inputField = document.getElementById(fieldId);
    if (inputField) {
        inputField.style.borderColor = 'var(--accent-red)';
    }
}

function clearErrors() {
    const errorSpans = document.querySelectorAll('.error-msg');
    errorSpans.forEach(span => {
        span.textContent = '';
        span.style.opacity = '0';
    });
    
    const inputs = document.querySelectorAll('.input-wrapper input, .input-wrapper select');
    inputs.forEach(input => {
        input.style.borderColor = 'var(--border-color)';
    });
}

function clearForm() {
    studentForm.reset();
    clearErrors();
}

// Toast Notifications System
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const iconName = type === 'success' ? 'check-circle' : 'alert-circle';
    
    toast.innerHTML = `
        <i data-lucide="${iconName}" class="toast-icon"></i>
        <div class="toast-message">${escapeHTML(message)}</div>
    `;
    
    toastContainer.appendChild(toast);
    lucide.createIcons();
    
    // Automatically remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

// HTML Escaping Utility to prevent XSS injection
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
