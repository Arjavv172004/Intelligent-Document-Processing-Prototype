// Main JavaScript for the Intelligent Document Processor

// Global variables
let currentFile = null;
let isProcessing = false;

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const previewSection = document.getElementById('previewSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const successModal = document.getElementById('successModal');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    animateOnScroll();
});

function initializeApp() {
    // Add smooth scrolling to navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Initialize tooltips and animations
    initializeAnimations();
}

function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Window events
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function processFile(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid file type (JPG, PNG, or PDF)');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return;
    }
    
    currentFile = file;
    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Show preview
        showPreview(file);
        
        // Start processing
        extractData(data.filepath);
    })
    .catch(error => {
        hideLoading();
        showError(error.message);
    });
}

function extractData(filepath) {
    showProcessing();
    
    fetch('/extract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filepath: filepath })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        showResults(data.data);
        showSuccess('Document processed successfully!');
    })
    .catch(error => {
        hideLoading();
        showError(error.message);
    });
}

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewImage = document.getElementById('previewImage');
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        previewSection.classList.add('fade-in');
    };
    reader.readAsDataURL(file);
}

function showProcessing() {
    processingSection.style.display = 'block';
    processingSection.classList.add('fade-in');
    
    // Animate progress
    animateProgress();
}

function animateProgress() {
    const progressFill = document.getElementById('progressFill');
    const steps = document.querySelectorAll('.step');
    
    let progress = 0;
    let currentStep = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;
        
        progressFill.style.width = progress + '%';
        
        // Update steps
        if (progress > 25 && currentStep === 0) {
            steps[0].classList.remove('active');
            steps[1].classList.add('active');
            currentStep = 1;
        } else if (progress > 50 && currentStep === 1) {
            steps[1].classList.remove('active');
            steps[2].classList.add('active');
            currentStep = 2;
        } else if (progress > 75 && currentStep === 2) {
            steps[2].classList.remove('active');
            steps[3].classList.add('active');
            currentStep = 3;
        }
        
        if (progress >= 100) {
            clearInterval(interval);
        }
    }, 200);
}

function showResults(data) {
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = '';
    
    // Create table rows for extracted data
    const fields = [
        { label: 'Document Type', value: data.document_type, confidence: '95%' },
        { label: 'Company Name', value: data.company_name, confidence: '88%' },
        { label: 'Invoice Number', value: data.invoice_number, confidence: '92%' },
        { label: 'Date', value: data.date, confidence: '90%' },
        { label: 'Amount', value: data.amount, confidence: '94%' },
        { label: 'Tax', value: data.tax, confidence: '87%' }
    ];
    
    fields.forEach(field => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${field.label}</td>
            <td>${field.value || 'Not detected'}</td>
            <td>
                <span class="confidence-badge ${getConfidenceClass(field.confidence)}">
                    ${field.confidence}
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function getConfidenceClass(confidence) {
    const value = parseInt(confidence);
    if (value >= 90) return 'high';
    if (value >= 70) return 'medium';
    return 'low';
}

function showLoading() {
    loadingOverlay.classList.add('show');
    isProcessing = true;
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
    isProcessing = false;
}

function showSuccess(message) {
    document.getElementById('successMessage').textContent = message;
    successModal.classList.add('show');
    
    setTimeout(() => {
        successModal.classList.remove('show');
    }, 3000);
}

function showError(message) {
    // Create error notification
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function closePreview() {
    previewSection.style.display = 'none';
    previewSection.classList.remove('fade-in');
}

function closeModal() {
    successModal.classList.remove('show');
}

function exportCSV() {
    if (!currentFile) {
        showError('No data to export');
        return;
    }
    
    window.location.href = '/export_csv';
}

function sendToAutomation() {
    if (!currentFile) {
        showError('No data to send');
        return;
    }
    
    showLoading();
    
    fetch('/simulate_automation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showSuccess(`Data sent to automation system! ID: ${data.automation_id}`);
        } else {
            showError(data.message || 'Failed to send data');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Failed to send data to automation system');
    });
}

function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({
        behavior: 'smooth'
    });
}

function handleScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
}

function handleResize() {
    // Handle responsive adjustments
    const isMobile = window.innerWidth < 768;
    
    if (isMobile) {
        // Mobile-specific adjustments
        document.body.classList.add('mobile');
    } else {
        document.body.classList.remove('mobile');
    }
}

function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .metric-card, .chart-card').forEach(el => {
        observer.observe(el);
    });
}

function animateOnScroll() {
    // Add staggered animation delays
    const elements = document.querySelectorAll('.feature-card');
    elements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Add CSS for error notifications
const style = document.createElement('style');
style.textContent = `
    .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fee2e2;
        border: 1px solid #fecaca;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #dc2626;
    }
    
    .notification-content button {
        background: none;
        border: none;
        color: #dc2626;
        cursor: pointer;
        padding: 0.25rem;
    }
    
    .confidence-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .confidence-badge.high {
        background: #dcfce7;
        color: #166534;
    }
    
    .confidence-badge.medium {
        background: #fef3c7;
        color: #92400e;
    }
    
    .confidence-badge.low {
        background: #fee2e2;
        color: #dc2626;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);
