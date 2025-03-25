// Global variables to store references and state
let autoGenerateInterval = null;
let generationData = null;
let messageCount = 0;
let startTime = null;
let isGenerating = false;
let nextGenerationTime = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auto Generate script loaded');
    
    // Wait a bit for the page to fully render before inserting our UI
    setTimeout(function() {
        // Attempt to find the right place to insert our auto-generation UI
        insertAutoGenerationUI();
    }, 500);
});

// Function to insert auto-generation UI into the page regardless of its structure
function insertAutoGenerationUI() {
    console.log('Attempting to insert auto-generation UI');
    
    // Look for different possible container elements
    const possibleContainers = [
        document.querySelector('.row'),                              // Standard row container
        document.querySelector('main'),                              // Main content area
        document.querySelector('.container'),                        // Bootstrap container
        document.querySelector('body')                               // Last resort - body element
    ];
    
    // Find the first valid container
    let container = null;
    for (const candidate of possibleContainers) {
        if (candidate) {
            container = candidate;
            break;
        }
    }
    
    if (!container) {
        console.error('Could not find a suitable container for auto-generation UI');
        return;
    }
    
    // Create auto-generation UI elements
    const autoGenContainer = document.createElement('div');
    autoGenContainer.className = 'auto-generation-container card shadow mb-4';
    autoGenContainer.style.marginTop = '20px';
    autoGenContainer.innerHTML = `
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="fas fa-robot me-2"></i>Automatic Data Generation</h5>
        </div>
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">Generation Interval</label>
                <div class="row g-2">
                    <div class="col-md-6">
                        <input type="number" id="gen-interval" class="form-control" min="1" value="10">
                    </div>
                    <div class="col-md-6">
                        <select id="interval-unit" class="form-select">
                            <option value="seconds">Seconds</option>
                            <option value="minutes">Minutes</option>
                            <option value="hours">Hours</option>
                        </select>
                    </div>
                </div>
                <small class="form-text text-muted">
                    How frequently to automatically generate and send data
                </small>
            </div>
            
            <div id="auto-generate-controls" class="d-grid gap-2">
                <button id="start-auto-generate" class="btn btn-success">
                    <i class="fas fa-play me-2"></i>Start Auto-Generate
                </button>
            </div>
            
            <div id="auto-generate-status" class="mt-3" style="display: none;">
                <div class="alert alert-success mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div><i class="fas fa-sync fa-spin me-2"></i>Auto-generating data...</div>
                        <div class="badge bg-primary" id="next-gen-time">Next: 10s</div>
                    </div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-6">Started at:</div>
                    <div class="col-6 text-end" id="start-time"></div>
                </div>
                <div class="row mb-2">
                    <div class="col-6">Messages sent:</div>
                    <div class="col-6 text-end" id="messages-sent">0</div>
                </div>
                <div class="row mb-2">
                    <div class="col-6">Running time:</div>
                    <div class="col-6 text-end" id="running-time">00:00</div>
                </div>
                
                <div class="d-grid">
                    <button id="stop-auto-generate" class="btn btn-danger">
                        <i class="fas fa-stop me-2"></i>Stop Auto-Generate
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add the auto-generation UI to the page
    container.appendChild(autoGenContainer);
    
    // Set up event handlers
    document.getElementById('start-auto-generate').addEventListener('click', startAutoGenerate);
    document.getElementById('stop-auto-generate').addEventListener('click', stopAutoGenerate);
    
    console.log('Auto-generation UI inserted');
}

// Function to start auto-generation
function startAutoGenerate() {
    // Don't start if already generating
    if (isGenerating) return;
    
    console.log('Starting auto-generation process...');
    
    // Reset counters and state
    messageCount = 0;
    startTime = new Date();
    isGenerating = true;
    
    // Try to find the form that contains the device name and data type fields
    const allForms = document.querySelectorAll('form');
    let deviceNameInput = null;
    let dataTypeSelect = null;
    let csrfTokenInput = null;
    let formUrl = window.location.href;
    
    // Try to find form fields from any form on the page
    for (const form of allForms) {
        // Look for device name input (text input or something similar)
        const possibleInputs = form.querySelectorAll('input[type="text"]');
        for (const input of possibleInputs) {
            if (input.name === 'device_name' || 
                input.id === 'device_name' || 
                input.placeholder?.toLowerCase().includes('device') ||
                input.labels?.length > 0 && Array.from(input.labels).some(label => 
                    label.textContent.toLowerCase().includes('device')
                )) {
                deviceNameInput = input;
                break;
            }
        }
        
        // Look for data type select
        const possibleSelects = form.querySelectorAll('select');
        for (const select of possibleSelects) {
            if (select.name === 'data_type' || select.id === 'data_type') {
                dataTypeSelect = select;
                break;
            }
        }
        
        // Look for CSRF token
        const hiddenInputs = form.querySelectorAll('input[type="hidden"]');
        for (const hidden of hiddenInputs) {
            if (hidden.name === 'csrf_token' || hidden.name.includes('csrf')) {
                csrfTokenInput = hidden;
                break;
            }
        }
        
        // If form has action attribute, use it
        if (form.action) {
            formUrl = form.action;
        }
        
        // If we found both fields in this form, break out of the loop
        if (deviceNameInput && dataTypeSelect) {
            break;
        }
    }
    
    // If we couldn't find the device name, try other strategies
    if (!deviceNameInput) {
        // Look for any input that might be the device name
        const textInputs = document.querySelectorAll('input[type="text"]');
        if (textInputs.length > 0) {
            deviceNameInput = textInputs[0]; // Use the first text input as a guess
        }
        
        if (!deviceNameInput) {
            // Look for a field with a label containing "device"
            const allLabels = document.querySelectorAll('label');
            for (const label of allLabels) {
                if (label.textContent.toLowerCase().includes('device')) {
                    if (label.htmlFor) {
                        deviceNameInput = document.getElementById(label.htmlFor);
                        if (deviceNameInput) break;
                    }
                }
            }
        }
    }
    
    // If we couldn't find the data type, use a default
    if (!dataTypeSelect) {
        // Look for any select element
        const selects = document.querySelectorAll('select');
        if (selects.length > 0) {
            dataTypeSelect = selects[0]; // Use the first select as a guess
        } else {
            // Create a fake data type object with a default value
            dataTypeSelect = { value: 'telemetry' };
        }
    }
    
    // If we still can't find the device name, we can't continue
    if (!deviceNameInput) {
        showError("Could not find device name input field.");
        stopAutoGenerate();
        return;
    }
    
    // Store critical data that we'll need for all future requests
    generationData = {
        deviceName: deviceNameInput.value,
        dataType: dataTypeSelect.value || 'telemetry',
        csrfToken: csrfTokenInput ? csrfTokenInput.value : null,
        url: formUrl
    };
    
    console.log('Stored form data for auto-generation:', generationData);
    
    // Get generation interval
    const intervalValue = parseInt(document.getElementById('gen-interval').value);
    const intervalUnit = document.getElementById('interval-unit').value;
    
    if (isNaN(intervalValue) || intervalValue < 1) {
        showError("Invalid interval. Please enter a value of at least 1.");
        stopAutoGenerate();
        return;
    }
    
    // Calculate milliseconds
    let intervalMs = intervalValue * 1000; // Default to seconds
    if (intervalUnit === 'minutes') {
        intervalMs = intervalValue * 60 * 1000;
    } else if (intervalUnit === 'hours') {
        intervalMs = intervalValue * 60 * 60 * 1000;
    }
    
    // Update UI
    document.getElementById('auto-generate-controls').style.display = 'none';
    document.getElementById('auto-generate-status').style.display = 'block';
    document.getElementById('start-time').textContent = formatTime(startTime);
    
    // Generate data immediately
    generateData(true).then(() => {
        console.log('Initial data generation successful');
    }).catch(error => {
        console.error('Error in initial data generation:', error);
        showError(`Error in initial data generation: ${error.message}`);
    });
    
    // Set next generation time
    nextGenerationTime = new Date(Date.now() + intervalMs);
    updateNextGenerationTime();
    
    // Set up the interval for future generations
    autoGenerateInterval = setInterval(() => {
        if (!isGenerating) {
            console.log('Auto-generation stopped, clearing interval');
            clearInterval(autoGenerateInterval);
            autoGenerateInterval = null;
            return;
        }
        
        generateData(true).then(() => {
            console.log('Periodic data generation successful');
        }).catch(error => {
            console.error('Error in periodic data generation:', error);
            showError(`Error in data generation: ${error.message}`);
        });
        
        // Update next generation time regardless of success/failure
        nextGenerationTime = new Date(Date.now() + intervalMs);
        updateNextGenerationTime();
    }, intervalMs);
    
    // Set up timer to update running time display
    const runtimeInterval = setInterval(() => {
        if (!isGenerating) {
            clearInterval(runtimeInterval);
            return;
        }
        updateRuntime();
        updateNextGenerationTime();
    }, 1000);
    
    console.log(`Auto-generation started with interval: ${intervalMs}ms`);
}

// Function to stop auto-generation
function stopAutoGenerate() {
    console.log('Stopping auto-generation...');
    
    // Set flag first to prevent any new operations
    isGenerating = false;
    
    // Clear the timer
    if (autoGenerateInterval) {
        clearInterval(autoGenerateInterval);
        autoGenerateInterval = null;
    }
    
    // Reset UI
    document.getElementById('auto-generate-controls').style.display = 'block';
    document.getElementById('auto-generate-status').style.display = 'none';
    
    // Clear stored data
    generationData = null;
    
    console.log('Auto-generation stopped. Total messages sent:', messageCount);
}

// Function to generate data
async function generateData(isAuto = false) {
    return new Promise((resolve, reject) => {
        console.log('Starting data generation process...');
        
        try {
            // For auto-generation, use the stored data
            if (isAuto) {
                if (!generationData) {
                    const error = new Error("No generation data available!");
                    console.error(error);
                    reject(error);
                    return;
                }
                
                // Create form data from stored values
                const formData = new FormData();
                formData.append('device_name', generationData.deviceName);
                formData.append('data_type', generationData.dataType);
                formData.append('timestamp', Date.now().toString());
                if (generationData.csrfToken) {
                    formData.append('csrf_token', generationData.csrfToken);
                }
                
                // Use fetch for the request with appropriate error handling
                console.log('Sending AJAX request to:', generationData.url);
                
                fetch(generationData.url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Cache-Control': 'no-cache'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    
                    // Try to parse as JSON, but don't fail if it's not JSON
                    return response.text().then(text => {
                        try {
                            return JSON.parse(text);
                        } catch (e) {
                            // If not JSON, create a basic success object
                            return { success: true };
                        }
                    });
                })
                .then(data => {
                    console.log("Auto-generation success:", data);
                    
                    // Update counters and UI only if we're still generating
                    if (isGenerating) {
                        messageCount++;
                        document.getElementById('messages-sent').textContent = messageCount;
                        
                        // Update the CSRF token if provided
                        if (data.csrf_token) {
                            generationData.csrfToken = data.csrf_token;
                        }
                    }
                    
                    resolve(data);
                })
                .catch(error => {
                    console.error("Error during auto-generation:", error);
                    reject(error);
                });
            } else {
                // For manual generation, use the existing form submission logic
                const form = document.querySelector('form');
                if (!form) {
                    const error = new Error("No form found on the page!");
                    console.error(error);
                    reject(error);
                    return;
                }
                
                // Add timestamp to form
                let timestampInput = form.querySelector('input[name="timestamp"]');
                if (!timestampInput) {
                    timestampInput = document.createElement('input');
                    timestampInput.type = 'hidden';
                    timestampInput.name = 'timestamp';
                    form.appendChild(timestampInput);
                }
                timestampInput.value = Date.now().toString();
                
                // Submit the form via AJAX
                const formData = new FormData(form);
                const xhr = new XMLHttpRequest();
                xhr.open('POST', form.action || window.location.pathname);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            console.log("Data generated and sent successfully:", response);
                            resolve(response);
                        } catch (e) {
                            console.log("Data generated and sent successfully.");
                            resolve({});
                        }
                    } else {
                        const error = new Error(`Error generating data: ${xhr.statusText}`);
                        console.error(error);
                        reject(error);
                    }
                };
                xhr.onerror = function() {
                    const error = new Error("Network error occurred when sending data");
                    console.error(error);
                    reject(error);
                };
                xhr.send(formData);
            }
        } catch (error) {
            console.error("Unexpected error in generateData:", error);
            reject(error);
        }
    });
}

// Function to show error messages
function showError(message) {
    console.error(message);
    
    // Try to find or create an error alert
    let errorAlert = document.getElementById('auto-error-alert');
    
    if (!errorAlert) {
        errorAlert = document.createElement('div');
        errorAlert.id = 'auto-error-alert';
        errorAlert.className = 'alert alert-danger mt-3';
        
        // Add it to the status panel if available
        const statusPanel = document.getElementById('auto-generate-status');
        if (statusPanel) {
            statusPanel.appendChild(errorAlert);
        } else {
            // Otherwise add it to the auto-generation container
            const container = document.querySelector('.auto-generation-container');
            if (container) {
                container.appendChild(errorAlert);
            }
        }
    }
    
    errorAlert.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
    errorAlert.style.display = 'block';
    
    // Hide it after 5 seconds
    setTimeout(() => {
        errorAlert.style.display = 'none';
    }, 5000);
}

// Function to update the next generation time display
function updateNextGenerationTime() {
    if (!isGenerating || !nextGenerationTime) return;
    
    const nextGenElement = document.getElementById('next-gen-time');
    if (nextGenElement) {
        const now = new Date();
        const timeLeft = Math.max(0, nextGenerationTime.getTime() - now.getTime());
        const secondsLeft = Math.ceil(timeLeft / 1000);
        
        nextGenElement.textContent = `Next: ${secondsLeft}s`;
    }
}

// Function to update the runtime display
function updateRuntime() {
    if (!isGenerating || !startTime) return;
    
    const now = new Date();
    const diff = now - startTime;
    
    // Calculate minutes and seconds
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    // Format as MM:SS
    const timeDisplay = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    document.getElementById('running-time').textContent = timeDisplay;
}

// Helper function to format a date object to a readable time string
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
