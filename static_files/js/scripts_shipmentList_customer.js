document.addEventListener('DOMContentLoaded', () => {
    // === Element Selectors ===
    const tableContainer = document.getElementById('shipmentTableContainer');
    const table = document.getElementById('shipmentTable');
    const headers = table.querySelectorAll('th');
    const totalRowsSpan = document.getElementById('totalRows');
    const totalTickedSpan = document.getElementById('totalTicked');
    const messageBox = document.getElementById('messageBox');
    const selectAllDataBtn = document.getElementById('selectAllDataBtn');
    const MIN_WIDTH = 50;
    const fullScreenBtn = document.getElementById('fullScreenBtn');
    const mainContainer = document.querySelector('.main-container');
    // Add a variable to select the hidden input field at the beginning of the file
    const shipmentCellClicked = document.getElementById('id_clicked');
    updateIconNumbering();
    // === Helper Functions ===
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Display Django messages on page load
    const djangoMessages = document.querySelectorAll('.messages .alert');
    djangoMessages.forEach(msg => {
        const messageText = msg.textContent.trim();
        showMessage(messageText);
        msg.remove();
    });

    function updateTickedCountOptimistically(change) {
        const totalTickedSpan = document.getElementById('totalTicked');
        // Ensure totalTickedSpan is found and content is a number
        if (!totalTickedSpan) return;

        let currentCount = parseInt(totalTickedSpan.textContent.trim()) || 0;

        // Calculate new count, ensuring it doesn't go below zero
        currentCount = Math.max(0, currentCount + change);

        // IMMEDIATE UPDATE
        totalTickedSpan.textContent = currentCount;
    }

    function updateTotalRows() {
        if (totalRowsSpan) {
            totalRowsSpan.textContent = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
        }
    }

    function showMessage(text) {
        if (messageBox) {
            messageBox.textContent = text;
            messageBox.style.display = 'block';
            messageBox.style.opacity = '1';
            setTimeout(() => {
                messageBox.style.opacity = '0';
                setTimeout(() => messageBox.style.display = 'none', 500);
            }, 3000);
        }
    }

    function updateSelectAllBtn(tickedNos, totalCount) {
        if (selectAllDataBtn) {
            selectAllDataBtn.innerHTML = '';
            if (tickedNos.length > 0 && tickedNos.length === totalCount) {
                selectAllDataBtn.textContent = 'Remove All Data';
                selectAllDataBtn.setAttribute('data-action', 'remove');
                const icon = document.createElement('i');
                icon.classList.add('bi', 'bi-x-square-fill');
                selectAllDataBtn.prepend(icon);
            } else {
                selectAllDataBtn.textContent = 'Select All Data';
                selectAllDataBtn.removeAttribute('data-action');
                const icon = document.createElement('i');
                icon.classList.add('bi', 'bi-check-square-fill');
                selectAllDataBtn.prepend(icon);
            }
        }
    }

    function updateTickedCount(tickedNos, totalCount) {
        const totalTicked = document.getElementById('totalTicked');
        if (totalTicked) {
            totalTicked.textContent = tickedNos.length;
        }
        updateSelectAllBtn(tickedNos, totalCount);
        const checkboxes = document.querySelectorAll('input[name="selection"]');
        checkboxes.forEach(cb => {
            cb.checked = tickedNos.includes(parseInt(cb.value));
        });
        const selectAll = document.getElementById('id_selectall');
        if (selectAll) {
            const allPageCheckboxes = document.querySelectorAll('input[name="selection"]');
            selectAll.checked = allPageCheckboxes.length > 0 && Array.from(allPageCheckboxes).every(cb => tickedNos.includes(parseInt(cb.value)));
        }
    }

    function fetchTickedCount() {
        fetch('/main1/stick_ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ action: 'get' }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`fetchTickedCount failed: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateTickedCount(data.tickedNos || [], data.totalCount || 0);
            // Sync checkbox states and row highlights
            const checkboxes = document.querySelectorAll('input[name="selection"]');
            checkboxes.forEach(cb => {
                const isChecked = data.tickedNos.includes(parseInt(cb.value));
                cb.checked = isChecked;
                const row = cb.closest('tr');
                if (row) {
                    if (isChecked) {
                        row.classList.add('table-primary');
                    } else {
                        row.classList.remove('table-primary');
                    }
                }
            });
        })
        .catch(error => {
            console.error('fetchTickedCount error:', error);
            showMessage('Failed to sync selection state.');
        });
    }

    // Modify the core function to use the new URL
    function updateSelectionOnServer(action, payload) {
        const url = '/main1/stick_ajax/';
        return fetch(url, {  // Return the fetch promise
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ action: action, ...payload }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server failed to save selection: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update UI with server response if needed
            if (data.total_count !== undefined) {
                const totalTicked = document.getElementById('totalTicked');
                if (totalTicked) {
                    totalTicked.textContent = data.total_count;
                }
            }
            return data; // Return data for further chaining
        })
        .catch(error => {
            console.error('Selection update error:', error);
            throw error; // Rethrow for caller to handle
        });
    }
    fetchTickedCount();

    if (tableContainer) {
        let debounceTimeout = null;
        tableContainer.addEventListener('change', (event) => {
            const target = event.target;
            if (target.matches('input[name="selection"]')) {
                const shipmentId = parseInt(target.value);
                const originalChecked = target.checked; // Store original state for rollback
                const isChecked = target.checked; // This will be the new state

                // OPTIMISTIC UI: Update count and highlight immediately
                const countChange = isChecked ? 1 : -1;
                updateTickedCountOptimistically(countChange);

                const row = target.closest('tr');
                if (row) {
                    if (isChecked) {
                        row.classList.add('table-primary');
                    } else {
                        row.classList.remove('table-primary');
                    }
                }

                // ASYNCHRONOUS SERVER UPDATE with rollback on failure
                const tickedNos = isChecked ? [shipmentId] : [];
                const untickedNos = isChecked ? [] : [shipmentId];
                updateSelectionOnServer('update', { tickedNos, untickedNos })
                    .then(data => {
                        // Optional: Sync UI with server response if needed
                        if (data.total_count !== undefined) {
                            const totalTicked = document.getElementById('totalTicked');
                            if (totalTicked) {
                                totalTicked.textContent = data.total_count;
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Individual selection update failed:', error);
                        showMessage('Failed to update selection. Please try again.');

                        // ROLLBACK UI
                        target.checked = !isChecked; // Revert checkbox
                        updateTickedCountOptimistically(-countChange); // Revert count
                        if (row) {
                            if (!isChecked) { // Revert highlight
                                row.classList.add('table-primary');
                            } else {
                                row.classList.remove('table-primary');
                            }
                        }
                    });

            } else if (target.matches('#id_selectall')) {
                // Debounce rapid toggles
                if (debounceTimeout) {
                    clearTimeout(debounceTimeout);
                }
                debounceTimeout = setTimeout(() => {
                    const isChecked = target.checked;
                    const pageCheckboxes = document.querySelectorAll('input[name="selection"]');
                    const pageIds = Array.from(pageCheckboxes).map(cb => parseInt(cb.value));

                    // OPTIMISTIC UI: Update all checkboxes and count immediately
                    pageCheckboxes.forEach(cb => {
                        cb.checked = isChecked;
                        const row = cb.closest('tr');
                        if (row) {
                            if (isChecked) {
                                row.classList.add('table-primary');
                            } else {
                                row.classList.remove('table-primary');
                            }
                        }
                    });
                    const countChange = isChecked ? pageIds.length : -pageIds.length;
                    updateTickedCountOptimistically(countChange);

                    // ASYNCHRONOUS SERVER UPDATE with UI sync
                    updateSelectionOnServer('update', {
                        tickedNos: isChecked ? pageIds : [],
                        untickedNos: isChecked ? [] : pageIds
                    }).then(data => {
                        // Update UI with server response
                        const totalTicked = document.getElementById('totalTicked');
                        if (totalTicked && data.total_count !== undefined) {
                            totalTicked.textContent = data.total_count;
                        }
                        // Sync Select All Data button
                        updateSelectAllBtn(data.tickedNos || [], data.total_count || 0);
                    }).catch(error => {
                        console.error('Select all update failed:', error);
                        showMessage('Failed to update selection. Please try again.');
                        // Rollback UI
                        pageCheckboxes.forEach(cb => {
                            cb.checked = !isChecked;
                            const row = cb.closest('tr');
                            if (row) {
                                if (!isChecked) {
                                    row.classList.add('table-primary');
                                } else {
                                    row.classList.remove('table-primary');
                                }
                            }
                        });
                        updateTickedCountOptimistically(-countChange);
                    });
                }, 300); // 300ms debounce delay
            }
        });
    }

    if (selectAllDataBtn) {
        selectAllDataBtn.addEventListener('click', () => {
            // Determine the action by cleaning the button's text content for a safer comparison
            const buttonText = selectAllDataBtn.textContent.trim();
            const action = (buttonText.includes('Select All Data')) ? 'select_all' : 'clear';
            // ADD THIS LINE: Capture the current URL query parameters (filters)
            const currentQueryParams = window.location.search;
            // Pass currentQueryParams only for 'select_all'; for 'clear', no need
            const payload = (action === 'select_all') ? { currentQueryParams } : {};
            // Send the request to the server
            updateSelectionOnServer(action, payload)
            .then(data => {
                // Update UI with server response
                updateTickedCount(data.tickedNos || [], data.total_count || 0);

                // Manually re-apply row highlighting
                const checkboxes = document.querySelectorAll('input[name="selection"]');
                checkboxes.forEach(cb => {
                    const isChecked = data.tickedNos.includes(parseInt(cb.value));
                    cb.checked = isChecked;  // Ensure checkbox state is synced
                    const row = cb.closest('tr');
                    if (row) {
                        if (isChecked) {
                            row.classList.add('table-primary');
                        } else {
                            row.classList.remove('table-primary');
                        }
                    }
                });

                // Provide feedback
                if (action === 'select_all') {
                    showMessage('All filtered shipments selected successfully!');
                } else {
                    showMessage('All selections cleared successfully!');
                }
            })
            .catch(error => {
                showMessage('Failed to process selection update. Please try again.');
            });
        });
    }

    // Adjust the selector if your export button has a different ID in mainView2
    const exportButton = document.getElementById('exportBtn'); // ← change if needed, e.g., 'exportExcelBtn'

    if (exportButton) {
        exportButton.addEventListener('click', function(event) {
            event.preventDefault();

            // Get current ticked shipments from session
            fetch('/main1/stick_ajax/', {  // ← CHANGE THIS if mainView2 uses a different URL, e.g., '/main2/stick_ajax/'
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ action: 'get' }),
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.tickedNos.length === 0) {
                    showMessage('Please select at least one shipment to export.');
                    return;
                }

                // Get current visible row order from the table
                const visibleRows = Array.from(document.querySelectorAll('#shipmentTable tbody tr'))
                    .filter(row => row.style.display !== 'none');

                const currentOrderIds = visibleRows
                    .map(row => {
                        const checkbox = row.querySelector('input[name="selection"]');
                        return checkbox ? parseInt(checkbox.value) : null;
                    })
                    .filter(id => id !== null && data.tickedNos.includes(id));

                // Prepare form submission
                const form = document.getElementById('shipmentForm'); // ← adjust if form ID is different
                if (!form) {
                    console.error('Form with ID "shipmentForm" not found.');
                    return;
                }

                // allTickedNos
                let allTickedNosInput = form.querySelector('input[name="allTickedNos"]');
                if (!allTickedNosInput) {
                    allTickedNosInput = document.createElement('input');
                    allTickedNosInput.type = 'hidden';
                    allTickedNosInput.name = 'allTickedNos';
                    form.appendChild(allTickedNosInput);
                }
                allTickedNosInput.value = data.tickedNos.join(',');

                // Export trigger
                let exportActionInput = form.querySelector('input[name="exportExcelShipment"]');
                if (!exportActionInput) {
                    exportActionInput = document.createElement('input');
                    exportActionInput.type = 'hidden';
                    exportActionInput.name = 'exportExcelShipment';
                    exportActionInput.value = 'true';
                    form.appendChild(exportActionInput);
                }

                // NEW: Send exact visual order
                let orderIdsInput = form.querySelector('input[name="export_order_ids"]');
                if (!orderIdsInput) {
                    orderIdsInput = document.createElement('input');
                    orderIdsInput.type = 'hidden';
                    orderIdsInput.name = 'export_order_ids';
                    form.appendChild(orderIdsInput);
                }
                orderIdsInput.value = currentOrderIds.join(',');

                // Submit
                form.submit();

                // Cleanup UI
                document.querySelectorAll('input[name="selection"]').forEach(cb => {
                    cb.checked = false;
                    const row = cb.closest('tr');
                    if (row) row.classList.remove('table-primary');
                });
                document.getElementById('id_selectall')?.checked && (document.getElementById('id_selectall').checked = false);
                document.getElementById('totalTicked').textContent = '0';

                const selectAllDataBtn = document.getElementById('selectAllDataBtn');
                if (selectAllDataBtn) {
                    selectAllDataBtn.innerHTML = '';
                    selectAllDataBtn.textContent = 'Select All Data';
                    const icon = document.createElement('i');
                    icon.classList.add('bi', 'bi-check-square-fill');
                    selectAllDataBtn.prepend(icon);
                    selectAllDataBtn.removeAttribute('data-action');
                }

                showMessage(`${data.tickedNos.length} shipments exported in current screen order.`);
            })
            .catch(error => {
                console.error('Export failed:', error);
                showMessage('Failed to export. Please try again.');
            });
        });
    }
    // Listener for the page selection dropdown
    const pageSelect = document.getElementById('pageSelect');
    if (pageSelect) {
        pageSelect.addEventListener('change', function() {
            // Submitting the form will automatically use the value from the 'page' select field
            document.getElementById('pageSelectForm').submit();
        });
    }

    let isDraggingResize = false;
    let didResize = false;
    let currentResizingHeader = null;
    let startX, startWidth;

    headers.forEach(header => {
        header.addEventListener('mousedown', (e) => {
            const rect = header.getBoundingClientRect();
            const isResizing = Math.abs(e.clientX - rect.right) < 10;
            if (isResizing && header.classList.contains('resizable')) {
                e.preventDefault();
                e.stopPropagation();
                isDraggingResize = true;
                didResize = false;
                currentResizingHeader = header;
                startX = e.clientX;
                startWidth = header.offsetWidth;
                document.body.style.userSelect = 'none';
            }
        });
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDraggingResize || !currentResizingHeader) return;
        const newWidth = startWidth + (e.clientX - startX);
        if (newWidth >= MIN_WIDTH) {
            currentResizingHeader.style.width = `${newWidth}px`;
            didResize = true;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDraggingResize) {
            isDraggingResize = false;
            currentResizingHeader = null;
            document.body.style.userSelect = '';
        }
    });

    let initialRowsOrder = Array.from(document.querySelectorAll('#shipmentTable tbody tr'));
    let currentSortKey = null;
    let sortDirection = 'asc';

    function applyRowColors() {
        const dataRows = document.querySelectorAll('#shipmentTable tbody tr:not([style*="display: none"])');
        dataRows.forEach((row, index) => {
            row.style.backgroundColor = index % 2 === 0 ? '#ffffff' : '#f8f8f8';
        });
    }

    function sortTable(key) {
        const allHeaders = document.querySelectorAll('th.sortable-header');
        const tbody = document.querySelector('table#shipmentTable tbody');
        if (!tbody) return;

        const dataRows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"])'));

        if (currentSortKey === key) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortDirection = 'asc';
            currentSortKey = key;
        }

        const colIndex = Array.from(document.querySelectorAll('#shipmentTable th')).findIndex(th => th.dataset.sortKey === key);

        dataRows.sort((a, b) => {
            const aCell = a.cells[colIndex];
            const bCell = b.cells[colIndex];

            let aValue = aCell ? aCell.innerHTML.trim() : '';
            let bValue = bCell ? bCell.innerHTML.trim() : '';

            const cleanText = (text) => {
                if (!text) return '';
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = text;
                return tempDiv.textContent || tempDiv.innerText || '';
            };

            if (key === 'shipmentId') {
                const aLink = aCell.querySelector('a');
                const bLink = bCell.querySelector('a');
                aValue = aLink ? cleanText(aLink.textContent) : cleanText(aValue);
                bValue = bLink ? cleanText(bLink.textContent) : cleanText(bValue);
            } else {
                aValue = cleanText(aValue);
                bValue = cleanText(bValue);
            }

            if (!aValue && !bValue) return 0;
            if (!aValue) return sortDirection === 'asc' ? 1 : -1;
            if (!bValue) return sortDirection === 'asc' ? -1 : 1;

            if (['quantity', 'weight'].includes(key)) {
                const cleanNumber = (val) => parseFloat(val.replace(/[^\d.]/g, '')) || 0;
                const aNum = cleanNumber(aValue);
                const bNum = cleanNumber(bValue);
                return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }

            if (key === 'size') {
                const parseFirstNumber = (val) => {
                    if (!val) return 0;
                    const firstLine = val.split(/<br\s*\/?>/)[0].trim();
                    const match = firstLine.match(/[\d.]+/);
                    return match ? parseFloat(match[0]) : 0;
                };
                const aNum = parseFirstNumber(aValue);
                const bNum = parseFirstNumber(bValue);
                return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }

            if (['inDate', 'outDate'].includes(key)) {
                const parseYmdDate = (val) => {
                    if (!val) return new Date(0);
                    const year = val.substring(0, 4);
                    const month = val.substring(4, 6) - 1;
                    const day = val.substring(6, 8);
                    return new Date(year, month, day);
                };
                const aDate = parseYmdDate(aValue);
                const bDate = parseYmdDate(bValue);
                return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
            }

            let comparison = aValue.localeCompare(bValue, undefined, { sensitivity: 'base' });
            return sortDirection === 'asc' ? comparison : -comparison;
        });

        tbody.innerHTML = '';
        dataRows.forEach(row => tbody.appendChild(row));

        allHeaders.forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
            if (th.dataset.sortKey === key) {
                th.classList.add(`sorted-${sortDirection}`);
            }
        });

        applyRowColors();
    }

    document.addEventListener('click', (e) => {
        const th = e.target.closest('th.sortable-header');

        if (didResize) {
            didResize = false;
            return;
        }

        if (!th || isDraggingResize) {
            return;
        }

        const key = th.dataset.sortKey;
        if (key) {
            sortTable(key);
        }
    });

    let isDraggingScroll = false;
    let startXScroll, scrollLeft;

    if (tableContainer) {
        tableContainer.addEventListener('mousedown', (e) => {
            const rect = e.target.closest('th')?.getBoundingClientRect();
            const isResizing = rect && Math.abs(e.clientX - rect.right) < 10;
            if (isResizing || e.target.closest('.sortable-header')) return;
            isDraggingScroll = true;
            startXScroll = e.clientX - tableContainer.offsetLeft;
            scrollLeft = tableContainer.scrollLeft;
        });

        tableContainer.addEventListener('mouseleave', () => isDraggingScroll = false);
        tableContainer.addEventListener('mouseup', () => isDraggingScroll = false);

        tableContainer.addEventListener('mousemove', (e) => {
            if (!isDraggingScroll) return;
            e.preventDefault();
            const x = e.clientX - tableContainer.offsetLeft;
            tableContainer.scrollLeft = scrollLeft - (x - startXScroll) * 1.5;
        });
    }

    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            if (link.dataset.imageUrl) {
                document.querySelector('#imageModal .modal-image').src = link.dataset.imageUrl;
                document.querySelector('.modal-image-download').href = link.dataset.imageUrl;
            } else if (link.dataset.pdfUrl) {
                document.querySelector('#pdfModal .modal-pdf').src = link.dataset.pdfUrl;
                document.querySelector('.modal-pdf-fallback').href = link.dataset.pdfUrl;
            }
        });
    });

    const resetButton = document.getElementById('resetSortBtn');
    if (resetButton) {
        resetButton.addEventListener('click', () => {
            const tbody = document.querySelector('table#shipmentTable tbody');
            if (!tbody) return;
            tbody.innerHTML = '';
            initialRowsOrder.forEach(row => tbody.appendChild(row));
            headers.forEach(th => th.classList.remove('sorted-asc', 'sorted-desc'));
            currentSortKey = null;
            sortDirection = 'asc';
            applyRowColors();
        });
    }

    window.addEventListener('load', () => {
        headers.forEach(th => th.style.width = `${th.offsetWidth}px`);
        updateTotalRows();
        fetchTickedCount();

    });

    const backToTopBtn = document.getElementById('backToTopBtn');
    window.addEventListener('scroll', handleScroll);
    if (tableContainer) {
        tableContainer.addEventListener('scroll', handleScroll);
    }

    function handleScroll() {
        const isFullScreen = document.body.classList.contains('full-screen');
        const scrollElement = isFullScreen ? document.querySelector('.main-container') : tableContainer;

        if (backToTopBtn && scrollElement && scrollElement.scrollTop > 200) {
            backToTopBtn.style.display = 'flex';
        } else if (backToTopBtn) {
            backToTopBtn.style.display = 'none';
        }
    }

    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => {
            const isFullScreen = document.body.classList.contains('full-screen');
            const scrollElement = isFullScreen ? document.querySelector('.main-container') : tableContainer;
            if (scrollElement) {
                scrollElement.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        });
    }

    if (fullScreenBtn && mainContainer && tableContainer) {
        fullScreenBtn.addEventListener('click', () => {
            document.body.classList.toggle('full-screen');
            mainContainer.classList.toggle('full-screen');
            tableContainer.classList.toggle('full-screen');
            if (document.body.classList.contains('full-screen')) {
                fullScreenBtn.innerHTML = '<i class="bi bi-x-square-fill"></i> Exit Full screen';
                fullScreenBtn.classList.add('exit-full-screen');
            } else {
                fullScreenBtn.innerHTML = '<i class="bi bi-arrows-fullscreen"></i> Full screen';
                fullScreenBtn.classList.remove('exit-full-screen');
            }
        });
    }
    function updateIconNumbering() {
        // Get all table body rows
        const tableRows = document.querySelectorAll('#shipmentTable tbody tr');

        tableRows.forEach(row => {
            // Handle image numbering for the current row
            let imageCounter = 1;
            const imageLinks = row.querySelectorAll('.image-icon-container .image-link');
            imageLinks.forEach(link => {
                const numberSpan = link.querySelector('.image-number');
                if (numberSpan) {
                    numberSpan.textContent = imageCounter++;
                }
            });

            // Handle PDF numbering for the current row
            let pdfCounter = 1;
            const pdfLinks = row.querySelectorAll('.pdf-icon-container .pdf-link');
            pdfLinks.forEach(link => {
                const numberSpan = link.querySelector('.pdf-number');
                if (numberSpan) {
                    numberSpan.textContent = pdfCounter++;
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});