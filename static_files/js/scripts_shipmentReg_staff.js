// scripts_shipmentReg_staff.js

// Flatpickr configuration for both "IN" and "ON BOARD DATE"
const datePickerConfig = {
    dateFormat: 'Ymd', // Display and output as YYYYMMDD (e.g., "20250311")
    allowInput: true, // Allow manual typing
    onChange: function(selectedDates, dateStr, instance) {
        instance.element.value = dateStr; // Ensure YYYYMMDD
    },
    onClose: function(selectedDates, dateStr, instance) {
        if (dateStr && dateStr.length === 8 && /^\d{8}$/.test(dateStr)) {
            const year = dateStr.slice(0, 4);
            const month = dateStr.slice(4, 6);
            const day = dateStr.slice(6, 8);
            const date = new Date(year, month - 1, day);
            if (date.getFullYear() != year || date.getMonth() + 1 != month || date.getDate() != day) {
                // Using console.error instead of alert as alerts break the UI
                console.error('Invalid date! Please enter a valid date in YYYYMMDD format.');
                instance.clear();
            }
        } else if (dateStr && dateStr.length !== 8) {
            // Using console.error instead of alert as alerts break the UI
            console.error('Date must be in YYYYMMDD format (8 digits)!');
            instance.clear();
        }
    }
};


// Initialize Flatpickr for "IN"
flatpickr('#id_in_date', datePickerConfig);

// Initialize Flatpickr for "ON BOARD DATE"
flatpickr('#id_out_date', datePickerConfig);

document.addEventListener('DOMContentLoaded', () => {
    const pdfInput = document.getElementById('id_pdf_file');
    const imageInput = document.getElementById('id_image'); 
    const clearPdfButton = document.getElementById('id_clearPdf'); 
    const clearImageButton = document.getElementById('id_clearImage');
    
    // --- START: File Size Calculation and Button Control Logic ---

    const MAX_FILE_SIZE_MB = 50;
    // Conversion to bytes: 50 * 1024 * 1024
    const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024; 
    const saveButton = document.getElementById('id_save_button');
    const updateButton = document.getElementById('id_update_button');
    const uploadStatusDiv = document.getElementById('upload-status');

    /**
     * Calculates the total size of all selected files (PDF and Image).
     * @returns {number} Total size in bytes.
     */
    const calculateTotalFileSize = () => {
        let totalSize = 0;
        
        // Sum size of PDF files
        if (pdfInput && pdfInput.files) {
            for (const file of pdfInput.files) {
                totalSize += file.size;
            }
        }

        // Sum size of image files
        if (imageInput && imageInput.files) {
            for (const file of imageInput.files) {
                totalSize += file.size;
            }
        }

        return totalSize;
    };

    /**
     * Formats bytes into a human-readable string (MB/KB).
     * @param {number} bytes The size in bytes.
     * @returns {string} Formatted size string.
     */
    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = 2; // Decimal places
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    /**
     * Updates the status message and enables/disables the Save/Update buttons.
     */
    const updateFileUploadStatus = () => {
        const totalSize = calculateTotalFileSize();
        const formattedSize = formatBytes(totalSize);
        let statusText;
        let isOverLimit = totalSize > MAX_FILE_SIZE_BYTES;

        if (isOverLimit) {
            statusText = `<i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>
                          <span class="text-danger">Total Size: ${formattedSize} / ${MAX_FILE_SIZE_MB} MB. Too Large!</span>`;
            uploadStatusDiv.classList.remove('bg-success-subtle', 'text-success');
            uploadStatusDiv.classList.add('bg-danger-subtle', 'text-danger');
        } else {
            statusText = `<i class="bi bi-check-circle-fill text-success me-2"></i>
                          <span class="text-success">Total Size: ${formattedSize} / ${MAX_FILE_SIZE_MB} MB. OK.</span>`;
            uploadStatusDiv.classList.remove('bg-danger-subtle', 'text-danger');
            uploadStatusDiv.classList.add('bg-success-subtle', 'text-success');
        }
        
        // Update the status display
        uploadStatusDiv.innerHTML = statusText;

        // Enable or disable the action buttons
        if (saveButton) {
            saveButton.disabled = isOverLimit;
        }
        if (updateButton) {
            updateButton.disabled = isOverLimit;
        }
    };

    
    // --- Combined handler for visual and size update on file selection ---
    const updateVisualsAndSize = (event) => {
        const input = event.target;
        const wrapper = input.parentElement;
        
        // 1. Visual Update (Placeholder visibility)
        if (input.files.length > 0) {
            wrapper.classList.add('has-file');
        } else {
            wrapper.classList.remove('has-file');
        }
        
        // 2. Size Check and Button Control
        updateFileUploadStatus(); 
    };
    
    // Attach the main change handler to both file inputs
    if (pdfInput) {
        pdfInput.addEventListener('change', updateVisualsAndSize);
    }
    if (imageInput) {
        imageInput.addEventListener('change', updateVisualsAndSize);
    }
    
    // --- Handlers for Clear Buttons ---
    
    // Clear PDF handler
    if (clearPdfButton && pdfInput) {
        clearPdfButton.addEventListener('click', () => {
            pdfInput.value = ""; // Clears the file input selection
            pdfInput.parentElement.classList.remove('has-file'); // Clear visual state
            updateFileUploadStatus(); // Recalculate size and update button state
        });
    }

    // Clear Image handler
    if (clearImageButton && imageInput) {
        clearImageButton.addEventListener('click', () => {
            imageInput.value = ""; // Clears the file input selection
            imageInput.parentElement.classList.remove('has-file'); // Clear visual state
            updateFileUploadStatus(); // Recalculate size and update button state
        });
    }

    // Initial check on page load
    updateFileUploadStatus();

    // --- END: File Size Calculation and Button Control Logic ---

    // Handle paste event for all relevant text areas (remove quotes)
    const textAreas = [
        document.getElementById('id_docs'), // DOCS field
        document.getElementById('id_Order_No'), // Order No field (Corrected ID based on HTML)
        document.getElementById('id_size'), // SIZE field
        document.getElementById('id_memo'), // MEMO field (Not present in HTML, but kept for future-proofing)
        document.getElementById('id_remark'), // REMARK field
        document.getElementById('id_ASKno'), // Added ASKno (Not present in HTML, but kept for future-proofing)
        document.getElementById('id_POno'), // POno field (Not present in HTML, but kept for future-proofing)
    ];

    textAreas.forEach(textArea => {
        if (textArea) {
            textArea.addEventListener('paste', (e) => {
                // Prevent the default paste behavior
                e.preventDefault();

                // Get the pasted text from the clipboard
                const pastedText = (e.clipboardData || window.clipboardData).getData('text/plain');

                // Log the raw clipboard data for debugging
                console.log('Raw clipboard data:', JSON.stringify(pastedText));

                // Normalize the text: trim whitespace and normalize line endings
                let cleanedText = pastedText.trim().replace(/\r\n/g, '\n').replace(/\r/g, '\n');

                // Remove surrounding quotation marks (including curly quotes)
                const quoteTypes = ['"', '"', '"']; // Straight, left curly, right curly quotes
                quoteTypes.forEach(quote => {
                    if (cleanedText.startsWith(quote) && cleanedText.endsWith(quote)) {
                        cleanedText = cleanedText.slice(1, -1);
                    }
                });

                // Handle Excel's escaped quotes (e.g., "" for a single quote within the text)
                cleanedText = cleanedText.replace(/""/g, '"');

                // Remove quotes from individual lines and trim whitespace
                cleanedText = cleanedText.split('\n').map(line => {
                    let trimmedLine = line.trim();
                    quoteTypes.forEach(quote => {
                        if (trimmedLine.startsWith(quote) && trimmedLine.endsWith(quote)) {
                            trimmedLine = trimmedLine.slice(1, -1);
                        }
                    });
                    return trimmedLine;
                }).filter(line => line.length > 0).join('\n'); // Remove empty lines

                // Log the cleaned text for debugging
                console.log('Cleaned text:', JSON.stringify(cleanedText));

                // Get the current cursor position in the text area
                const startPos = textArea.selectionStart;
                const endPos = textArea.selectionEnd;
                const currentValue = textArea.value;

                // Insert the cleaned text at the cursor position
                textArea.value = currentValue.substring(0, startPos) + cleanedText + currentValue.substring(endPos);

                // Move the cursor to the end of the pasted text
                const newCursorPos = startPos + cleanedText.length;
                textArea.setSelectionRange(newCursorPos, newCursorPos);

                // Provide visual feedback
                textArea.style.borderColor = '#007bff'; // Highlight on paste
                setTimeout(() => {
                    textArea.style.borderColor = ''; // Reset after 500ms
                }, 500);
            });
        }
    });

    // Handle QTY field to remove decimal points and ensure whole numbers
    const qtyInput = document.getElementById('id_quanty');
    if (qtyInput) {
        qtyInput.addEventListener('input', (e) => {
            let value = e.target.value;

            // Remove any non-numeric characters except for the decimal point
            value = value.replace(/[^0-9.]/g, '');

            // Parse the value as a float and convert to an integer to remove decimals
            if (value !== '') {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                    value = Math.floor(numValue).toString(); // Remove decimal points (e.g., 1.0 -> 1, 0.0 -> 0)
                } else {
                    value = ''; // Clear the field if the input is invalid
                }
            }

            // Update the input field with the cleaned-up value
            e.target.value = value;
        });

        // Ensure the value is an integer on form submission
        qtyInput.closest('form').addEventListener('submit', (e) => {
            let value = qtyInput.value;
            if (value !== '') {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                    qtyInput.value = Math.floor(numValue).toString();
                } else {
                    qtyInput.value = '';
                }
            }
        });
    }
});
