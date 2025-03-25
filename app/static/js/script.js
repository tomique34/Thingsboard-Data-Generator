/**
 * Main JavaScript file for Thingsboard Data Generator
 */

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Thingsboard Data Generator initialized.');
    
    // Setup CSRF protection for AJAX requests if needed
    setupCSRF();
});

// Setup CSRF protection for AJAX requests
function setupCSRF() {
    // Get CSRF token from meta tag if present
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (!tokenMeta) return;
    
    const token = tokenMeta.getAttribute('content');
    
    // Add token to all AJAX requests
    document.addEventListener('fetch', function(e) {
        const options = e.detail?.options;
        if (options && options.method !== 'GET') {
            if (!options.headers) options.headers = {};
            options.headers['X-CSRFToken'] = token;
        }
    });
}
