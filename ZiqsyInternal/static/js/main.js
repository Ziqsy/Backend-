/**
 * Ziqsy Internal Admin System - Main JavaScript Utilities
 * Provides shared functionality across all pages
 */

// Global utilities
window.ZiqsyAdmin = {
    // Configuration
    config: {
        maxFileSize: 16 * 1024 * 1024, // 16MB
        supportedFileTypes: {
            csv: 'text/csv',
            excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            json: 'application/json',
            markdown: 'text/markdown'
        }
    },

    // Utility functions
    utils: {
        /**
         * Format file size in human readable format
         */
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        /**
         * Validate file type and size
         */
        validateFile: function(file) {
            const errors = [];
            
            // Check file size
            if (file.size > ZiqsyAdmin.config.maxFileSize) {
                errors.push(`File size exceeds maximum limit of ${ZiqsyAdmin.utils.formatFileSize(ZiqsyAdmin.config.maxFileSize)}`);
            }
            
            // Check file type
            const fileExtension = file.name.split('.').pop().toLowerCase();
            const validExtensions = ['csv', 'xlsx', 'xls', 'json', 'md'];
            
            if (!validExtensions.includes(fileExtension)) {
                errors.push(`File type .${fileExtension} is not supported. Supported types: ${validExtensions.join(', ')}`);
            }
            
            return {
                valid: errors.length === 0,
                errors: errors
            };
        },

        /**
         * Show loading state on button
         */
        showLoading: function(button, text = 'Loading...') {
            if (!button) return;
            
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${text}`;
            button.disabled = true;
        },

        /**
         * Hide loading state on button
         */
        hideLoading: function(button) {
            if (!button || !button.dataset.originalText) return;
            
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
            delete button.dataset.originalText;
        },

        /**
         * Debounce function calls
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Sanitize HTML to prevent XSS
         */
        sanitizeHtml: function(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        },

        /**
         * Copy text to clipboard
         */
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                return navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return Promise.resolve();
            }
        }
    },

    // Form handling utilities
    forms: {
        /**
         * Serialize form data to JSON
         */
        serializeToJson: function(form) {
            const formData = new FormData(form);
            const json = {};
            for (const [key, value] of formData.entries()) {
                json[key] = value;
            }
            return json;
        },

        /**
         * Reset form with confirmation
         */
        resetWithConfirmation: function(form, message = 'Are you sure you want to reset the form?') {
            if (confirm(message)) {
                form.reset();
                return true;
            }
            return false;
        },

        /**
         * Validate required fields
         */
        validateRequired: function(form) {
            const requiredFields = form.querySelectorAll('[required]');
            const errors = [];
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    errors.push(`${field.labels[0]?.textContent || field.name} is required`);
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            return {
                valid: errors.length === 0,
                errors: errors
            };
        }
    },

    // Data table utilities
    tables: {
        /**
         * Sort table by column
         */
        sortTable: function(table, columnIndex, ascending = true) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();
                
                // Try to parse as numbers
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return ascending ? aNum - bNum : bNum - aNum;
                } else {
                    return ascending ? 
                        aValue.localeCompare(bValue) : 
                        bValue.localeCompare(aValue);
                }
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        },

        /**
         * Filter table rows by search term
         */
        filterTable: function(table, searchTerm) {
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            const term = searchTerm.toLowerCase();
            
            let visibleCount = 0;
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(term)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            return visibleCount;
        }
    },

    // Notification system
    notifications: {
        /**
         * Show success notification
         */
        success: function(message) {
            this.show(message, 'success');
        },

        /**
         * Show error notification
         */
        error: function(message) {
            this.show(message, 'error');
        },

        /**
         * Show info notification
         */
        info: function(message) {
            this.show(message, 'info');
        },

        /**
         * Show notification
         */
        show: function(message, type = 'info') {
            const alertClass = type === 'error' ? 'alert-danger' : 
                             type === 'success' ? 'alert-success' : 'alert-info';
            
            const alert = document.createElement('div');
            alert.className = `alert ${alertClass} alert-dismissible fade show`;
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Find or create flash messages container
            let container = document.querySelector('.flash-messages');
            if (!container) {
                container = document.createElement('div');
                container.className = 'flash-messages';
                document.body.appendChild(container);
            }
            
            container.appendChild(alert);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    },

    // Local storage utilities
    storage: {
        /**
         * Set item in localStorage with expiration
         */
        setItem: function(key, value, expireInMinutes = null) {
            const item = {
                value: value,
                timestamp: Date.now(),
                expire: expireInMinutes ? Date.now() + (expireInMinutes * 60 * 1000) : null
            };
            localStorage.setItem(`ziqsy_${key}`, JSON.stringify(item));
        },

        /**
         * Get item from localStorage
         */
        getItem: function(key) {
            const itemStr = localStorage.getItem(`ziqsy_${key}`);
            if (!itemStr) return null;
            
            try {
                const item = JSON.parse(itemStr);
                
                // Check if expired
                if (item.expire && Date.now() > item.expire) {
                    localStorage.removeItem(`ziqsy_${key}`);
                    return null;
                }
                
                return item.value;
            } catch (e) {
                localStorage.removeItem(`ziqsy_${key}`);
                return null;
            }
        },

        /**
         * Remove item from localStorage
         */
        removeItem: function(key) {
            localStorage.removeItem(`ziqsy_${key}`);
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add global event listeners
    
    // File upload validation
    document.addEventListener('change', function(e) {
        if (e.target.type === 'file') {
            const file = e.target.files[0];
            if (file) {
                const validation = ZiqsyAdmin.utils.validateFile(file);
                if (!validation.valid) {
                    ZiqsyAdmin.notifications.error(validation.errors.join('<br>'));
                    // Reset the file input without setting value directly
                    e.target.form?.reset();
                }
            }
        }
    });
    
    // Form submission with loading states
    document.addEventListener('submit', function(e) {
        const submitButton = e.target.querySelector('button[type="submit"]');
        if (submitButton) {
            ZiqsyAdmin.utils.showLoading(submitButton);
        }
    });
    
    // Auto-resize textareas
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'TEXTAREA') {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        }
    });
    
    // Add sortable headers to tables
    document.querySelectorAll('table th').forEach((th, index) => {
        if (!th.classList.contains('no-sort')) {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function() {
                const table = this.closest('table');
                const isAscending = !this.classList.contains('sort-desc');
                
                // Remove sort classes from all headers
                table.querySelectorAll('th').forEach(header => {
                    header.classList.remove('sort-asc', 'sort-desc');
                });
                
                // Add sort class to current header
                this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
                
                // Sort table
                ZiqsyAdmin.tables.sortTable(table, index, isAscending);
            });
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save forms
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const form = document.querySelector('form:not([data-no-save])');
            if (form) {
                form.requestSubmit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.show');
            if (modal) {
                bootstrap.Modal.getInstance(modal)?.hide();
            }
        }
    });
    
    // Save form data to localStorage on input
    const debouncedSave = ZiqsyAdmin.utils.debounce(function(form) {
        const formData = ZiqsyAdmin.forms.serializeToJson(form);
        const formId = form.id || form.action || 'default';
        ZiqsyAdmin.storage.setItem(`form_${formId}`, formData, 60); // Save for 1 hour
    }, 1000);
    
    document.addEventListener('input', function(e) {
        const form = e.target.closest('form');
        if (form && !form.classList.contains('no-autosave')) {
            debouncedSave(form);
        }
    });
    
    // Restore form data from localStorage
    document.querySelectorAll('form:not(.no-autosave)').forEach(form => {
        const formId = form.id || form.action || 'default';
        const savedData = ZiqsyAdmin.storage.getItem(`form_${formId}`);
        
        if (savedData) {
            Object.keys(savedData).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && !field.value) {
                    field.value = savedData[key];
                }
            });
        }
    });
});

// Add CSS for sorting indicators
const style = document.createElement('style');
style.textContent = `
    th.sort-asc::after {
        content: ' ↑';
        color: var(--accent-mauve);
    }
    th.sort-desc::after {
        content: ' ↓';
        color: var(--accent-mauve);
    }
    .is-invalid {
        border-color: #dc3545 !important;
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZiqsyAdmin;
}
