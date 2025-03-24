// Client-side functionality for Thingsboard Data Generator

document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Dynamic form field visibility based on selected data type
    const dataTypeSelect = document.querySelector('select[name="data_type"]');
    if (dataTypeSelect) {
        const updateFormFields = function() {
            const selectedType = dataTypeSelect.value;
            const minValueField = document.querySelector('.mb-3:has(input[name="min_value"])');
            const maxValueField = document.querySelector('.mb-3:has(input[name="max_value"])');
            const optionsField = document.querySelector('.mb-3:has(input[name="options"])');
            
            if (selectedType === 'string') {
                // For string type, hide min/max fields and show options
                if (minValueField) minValueField.style.display = 'none';
                if (maxValueField) maxValueField.style.display = 'none';
                if (optionsField) optionsField.style.display = 'block';
            } else if (selectedType === 'boolean') {
                // For boolean type, hide all range fields
                if (minValueField) minValueField.style.display = 'none';
                if (maxValueField) maxValueField.style.display = 'none';
                if (optionsField) optionsField.style.display = 'none';
            } else {
                // For numeric types, show min/max and hide options
                if (minValueField) minValueField.style.display = 'block';
                if (maxValueField) maxValueField.style.display = 'block';
                if (optionsField) optionsField.style.display = 'none';
            }
        };
        
        // Call initially and add change listener
        updateFormFields();
        dataTypeSelect.addEventListener('change', updateFormFields);
    }
});
