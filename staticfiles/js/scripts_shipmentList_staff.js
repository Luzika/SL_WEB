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

    function updateDynamicTotals() {
        const totalPackagesSpan = document.getElementById('totalPackages');
        const totalWeightSpan = document.getElementById('totalWeight');
        
        if (!totalPackagesSpan || !totalWeightSpan) return;

        let totalPkgs = 0;
        let totalWgt = 0.0;

        // Look at all checked checkboxes
        const checkedBoxes = document.querySelectorAll('input[name="selection"]:checked');
        
        checkedBoxes.forEach(cb => {
            const row = cb.closest('tr');
            if (row) {
                // Based on your singleClickFunction logic:
                // QTY (Packages) is usually row.cells[8]
                // Weight is usually row.cells[11]
                // Note: Update these indices if your table columns are different!
                
                const pkgValue = row.cells[9].innerText.trim();
                const wgtValue = row.cells[12].innerText.trim().replace(/,/g, '');

                if (pkgValue) totalPkgs += parseInt(pkgValue) || 0;
                if (wgtValue) totalWgt += parseFloat(wgtValue) || 0;
            }
        });

        // Update the UI
        totalPackagesSpan.textContent = totalPkgs.toLocaleString();
        totalWeightSpan.textContent = totalWgt.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
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
            updateDynamicTotals();
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
                    updateDynamicTotals();

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

                    updateDynamicTotals();
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
            // 1. Send the request to the server
            updateSelectionOnServer(action, { currentQueryParams })
            .then(data => {
                // 2. CRITICAL: On success, call the function that syncs the UI
                //    This function updates the total count, the button text/icon, and the page's checkboxes.
                updateTickedCount(data.tickedNos || [], data.total_count || 0);

                // 3. Manually re-apply row highlighting (as updateTickedCount doesn't seem to do this)
                const checkboxes = document.querySelectorAll('input[name="selection"]');
                checkboxes.forEach(cb => {
                    const isChecked = data.tickedNos.includes(parseInt(cb.value));
                    const row = cb.closest('tr');
                    if (row) {
                        if (isChecked) {
                            row.classList.add('table-primary');
                        } else {
                            row.classList.remove('table-primary');
                        }
                    }
                });

                // 4. Provide feedback
                if (action === 'select_all') {
                    showMessage('All shipments selected successfully!');
                } else {
                    showMessage('All selections cleared successfully!');
                }

            })
            .catch(error => {
                showMessage('Failed to process selection update. Please try again.');
            });
        });
    }

    const exportButton = document.getElementById('exportBtn');
    if (exportButton) {
        exportButton.addEventListener('click', function(event) {
            event.preventDefault();
            fetch('/main1/stick_ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ action: 'get' }),
            }).then(response => response.json()).then(data => {
                if (data.tickedNos.length === 0) {
                    showMessage('Please select at least one shipment to export.');
                    return;
                }
                const form = document.getElementById('shipmentForm');
                if (!form) {
                    console.error('Form with ID "shipmentForm" not found.');
                    return;
                }
                let allTickedNosInput = form.querySelector('input[name="allTickedNos"]');
                if (!allTickedNosInput) {
                    allTickedNosInput = document.createElement('input');
                    allTickedNosInput.type = 'hidden';
                    allTickedNosInput.name = 'allTickedNos';
                    form.appendChild(allTickedNosInput);
                }
                allTickedNosInput.value = data.tickedNos.join(',');
                let exportActionInput = form.querySelector('input[name="exportExcelShipment"]');
                if (!exportActionInput) {
                    exportActionInput = document.createElement('input');
                    exportActionInput.type = 'hidden';
                    exportActionInput.name = 'exportExcelShipment';
                    exportActionInput.value = 'true';
                    form.appendChild(exportActionInput);
                }
                form.submit();
                const checkboxes = document.querySelectorAll('input[name="selection"]');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                });
                const selectAll = document.getElementById('id_selectall');
                if (selectAll) {
                    selectAll.checked = false;
                }
                if (typeof updateTotalTicked === 'function') {
                    updateTotalTicked();
                } else {
                    document.getElementById('totalTicked').textContent = '0';
                }
                const selectAllDataBtn = document.getElementById('selectAllDataBtn');
                if (selectAllDataBtn) {
                    selectAllDataBtn.textContent = 'Select All Data';
                    selectAllDataBtn.removeAttribute('data-action');
                    const icon = document.createElement('i');
                    icon.classList.add('bi', 'bi-check-square-fill');
                    selectAllDataBtn.prepend(icon);
                }
                showMessage(`${data.tickedNos.length} shipments were successfully exported.`);
            }).catch(error => {
                console.error('Fetch error:', error);
                showMessage('Failed to retrieve selected shipments.');
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

    // function sortTable(key) {
    //     const allHeaders = document.querySelectorAll('th.sortable-header');
    //     const tbody = document.querySelector('table#shipmentTable tbody');
    //     if (!tbody) return;

    //     const dataRows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"])'));

    //     if (currentSortKey === key) {
    //         sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    //     } else {
    //         sortDirection = 'asc';
    //         currentSortKey = key;
    //     }

    //     const colIndex = Array.from(document.querySelectorAll('#shipmentTable th')).findIndex(th => th.dataset.sortKey === key);

    //     dataRows.sort((a, b) => {
    //         const aCell = a.cells[colIndex];
    //         const bCell = b.cells[colIndex];

    //         let aValue = aCell ? aCell.innerHTML.trim() : '';
    //         let bValue = bCell ? bCell.innerHTML.trim() : '';

    //         const cleanText = (text) => {
    //             if (!text) return '';
    //             const tempDiv = document.createElement('div');
    //             tempDiv.innerHTML = text;
    //             return tempDiv.textContent || tempDiv.innerText || '';
    //         };

    //         if (key === 'shipmentId') {
    //             const aLink = aCell.querySelector('a');
    //             const bLink = bCell.querySelector('a');
    //             aValue = aLink ? cleanText(aLink.textContent) : cleanText(aValue);
    //             bValue = bLink ? cleanText(bLink.textContent) : cleanText(bValue);
    //         } else {
    //             aValue = cleanText(aValue);
    //             bValue = cleanText(bValue);
    //         }

    //         if (!aValue && !bValue) return 0;
    //         if (!aValue) return sortDirection === 'asc' ? 1 : -1;
    //         if (!bValue) return sortDirection === 'asc' ? -1 : 1;

    //         if (['quantity', 'weight'].includes(key)) {
    //             const cleanNumber = (val) => parseFloat(val.replace(/[^\d.]/g, '')) || 0;
    //             const aNum = cleanNumber(aValue);
    //             const bNum = cleanNumber(bValue);
    //             return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
    //         }

    //         if (key === 'size') {
    //             const parseFirstNumber = (val) => {
    //                 if (!val) return 0;
    //                 const firstLine = val.split(/<br\s*\/?>/)[0].trim();
    //                 const match = firstLine.match(/[\d.]+/);
    //                 return match ? parseFloat(match[0]) : 0;
    //             };
    //             const aNum = parseFirstNumber(aValue);
    //             const bNum = parseFirstNumber(bValue);
    //             return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
    //         }

    //         if (['inDate', 'outDate'].includes(key)) {
    //             const parseYmdDate = (val) => {
    //                 if (!val) return new Date(0);
    //                 const year = val.substring(0, 4);
    //                 const month = val.substring(4, 6) - 1;
    //                 const day = val.substring(6, 8);
    //                 return new Date(year, month, day);
    //             };
    //             const aDate = parseYmdDate(aValue);
    //             const bDate = parseYmdDate(bValue);
    //             return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
    //         }

    //         let comparison = aValue.localeCompare(bValue, undefined, { sensitivity: 'base' });
    //         return sortDirection === 'asc' ? comparison : -comparison;
    //     });

    //     tbody.innerHTML = '';
    //     dataRows.forEach(row => tbody.appendChild(row));

    //     allHeaders.forEach(th => {
    //         th.classList.remove('sorted-asc', 'sorted-desc');
    //         if (th.dataset.sortKey === key) {
    //             th.classList.add(`sorted-${sortDirection}`);
    //         }
    //     });

    //     applyRowColors();
    // }

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
    // === The singleclickfunction.js file - Modified to add file loading ===
    function singleClickFunction() {
        // This function is a placeholder for single-click actions.
        const shipmentTable = document.getElementById('shipmentTable');
        // Define the form container to scroll to
        const shipmentRegForm = document.querySelector('.shipmentBox');
        const shipmentCells = shipmentTable.getElementsByTagName('td');
        
        // Keep ALL your existing variable definitions (matching your HTML IDs)
        const ship_info_company = document.getElementById('id_prelistCompanies');
        const ship_info_vessel = document.getElementById('id_pickVessels');
        const ship_info_supplier = document.getElementById('id_supplier');
        const ship_info_IMP = document.getElementById('id_IMP_BL');
        const ship_info_EXP = document.getElementById('id_EXP_BL');
        const ship_info_orderNo = document.getElementById('id_Order_No');

        const ship_info_division = document.getElementById('id_division');
        const ship_info_quantity = document.getElementById('id_quanty');
        const ship_info_weight = document.getElementById('id_weight');
        const ship_info_cpacking = document.getElementById('id_c_packing');
        const ship_info_units = document.getElementById('id_pickUnits');
        const ship_info_size = document.getElementById('id_size');
        const ship_info_docs = document.getElementById('id_docs');

        const ship_info_indate = document.getElementById('id_in_date');
        const ship_info_warehouse = document.getElementById('id_pickWH1');
        const ship_info_by = document.getElementById('id_by');
        const ship_info_port = document.getElementById('id_port');
        const ship_info_onboarddate = document.getElementById('id_out_date');
        const ship_info_remarks = document.getElementById('id_remark');

        for (let i = 0; i < shipmentCells.length; i++) {
            let cell = shipmentCells[i];
            cell.onclick = function(e) {
                // Prevent form population if clicking the Shipment ID link
                if (e.target.closest('.shipment-id-link')) {
                    return; // Let the link navigate to tracking page
                }

                let rowID = this.parentNode.rowIndex;
                let rowSelected = shipmentTable.getElementsByTagName('tr')[rowID];
                shipmentCellClicked.value = rowSelected.cells[0].firstElementChild.value;
                let pivotCell2 = rowSelected.cells[2]; // Company
                let pivotCell3 = rowSelected.cells[3]; // Vessel

                if (cell === pivotCell2 || cell === pivotCell3) {
                    // === YOUR EXISTING DATA COLLECTION (UNCHANGED) ===
                    let company = rowSelected.cells[2].innerText;
                    let vessel = rowSelected.cells[3].innerText;
                    let doc = rowSelected.cells[4].innerText;
                    let orderNo = rowSelected.cells[5].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim();
                    let supplier = rowSelected.cells[6].innerText;
                    let Cpacking = rowSelected.cells[7].innerText;
                    let quantity = rowSelected.cells[8].innerText;
                    let unit = rowSelected.cells[9].innerText;
                    let size = rowSelected.cells[10].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim();
                    let weight = rowSelected.cells[11].innerText;
                    let division = rowSelected.cells[12].innerText;
                    let indate = rowSelected.cells[13].innerText;
                    let warehouse = rowSelected.cells[14].innerText;
                    let by = rowSelected.cells[15].innerText;
                    let imp_bl = rowSelected.cells[16].innerText;
                    let port = rowSelected.cells[17].innerText;
                    let onboarddate = rowSelected.cells[18].innerText;
                    let remark = rowSelected.cells[19].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim();
                    let exp_bl = rowSelected.cells[20].innerText;

                    indate = String(indate.trim());
                    onboarddate = String(onboarddate.trim());

                    // === YOUR EXISTING FORM POPULATION (UNCHANGED) ===
                    ship_info_company.value = company;
                    ship_info_vessel.value = vessel;
                    ship_info_supplier.value = supplier;
                    ship_info_IMP.value = imp_bl;
                    ship_info_EXP.value = exp_bl;
                    ship_info_orderNo.value = orderNo;
                    ship_info_division.value = division.trim();
                    ship_info_quantity.value = quantity;
                    ship_info_weight.value = weight;
                    ship_info_cpacking.value = Cpacking;
                    ship_info_units.value = unit;
                    ship_info_size.value = size;
                    ship_info_docs.value = doc;
                    ship_info_indate.value = extractDate(indate);
                    ship_info_warehouse.value = warehouse;
                    ship_info_by.value = by;
                    ship_info_port.value = port;
                    ship_info_onboarddate.value = onboarddate.length ? extractDate(onboarddate) : '';
                    ship_info_remarks.value = remark;

                    // === NEW: Load Existing Files via AJAX ===
                    const shipmentId = rowSelected.cells[0].firstElementChild.value;
                    
                    // Clear existing file containers
                    const pdfContainer = document.getElementById('existing_pdfs_container');
                    const imageContainer = document.getElementById('existing_images_container');
                    const filesToDeleteInput = document.getElementById('files_to_delete');
                    if (pdfContainer) pdfContainer.innerHTML = '<p class="text-muted m-0">Loading PDF files...</p>';
                    if (imageContainer) imageContainer.innerHTML = '<p class="text-muted m-0">Loading Image files...</p>';
                    if (filesToDeleteInput) filesToDeleteInput.value = '';

                    // AJAX to fetch files only
                    fetch(`/main1/get_shipment_details_ajax/?shipment_id=${shipmentId}`, {
                        method: 'GET',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => {
                        if (!response.ok) throw new Error(`HTTP ${response.status}`);
                        return response.json();
                    })
                    // === REPLACE the AJAX section in your singleClickFunction() ===
                    .then(data => {
                        console.log('FULL AJAX RESPONSE:', data);  // ADD THIS LINE
                        console.log('FILES ARRAY:', data.files);   // ADD THIS LINE
                        console.log('FILES LENGTH:', data.files ? data.files.length : 'NO FILES');  // ADD THIS LINE
                        
                        if (data.status === 'success') {
                            // Display existing files
                            displayExistingFiles(data.files || []);  // Ensure empty array if null
                        } else {
                            console.error('File load error:', data.message);
                            // Reset containers to empty
                            if (pdfContainer) pdfContainer.innerHTML = '<p class="text-muted m-0">No PDF files loaded.</p>';
                            if (imageContainer) imageContainer.innerHTML = '<p class="text-muted m-0">No Image files loaded.</p>';
                        }
                    })
                    .catch(error => {
                        console.error('AJAX file load error:', error);
                        // Reset containers to empty on error
                        if (pdfContainer) pdfContainer.innerHTML = '<p class="text-muted m-0">No PDF files loaded.</p>';
                        if (imageContainer) imageContainer.innerHTML = '<p class="text-muted m-0">No Image files loaded.</p>';
                    });

                    // === YOUR EXISTING SCROLL (UNCHANGED) ===
                    shipmentRegForm.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            };
        }
    }
    // Call the function here to activate the click listener
    singleClickFunction();

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

    const deleteButton = document.getElementById('deleteShipment');
    if (deleteButton) {
        let isDeleting = false; // Prevent multiple clicks
        deleteButton.addEventListener('click', function(event) {
            event.preventDefault();
            if (isDeleting) return; // Block if already processing
            isDeleting = true;

            // Fetch selected IDs
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
                    throw new Error(`Failed to fetch selections: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const tickedNos = data.tickedNos;
                if (tickedNos.length === 0) {
                    showMessage('Please select at least one shipment to delete.');
                    isDeleting = false;
                    return;
                }

                // Warn about missing IDs
                if (data.missingNos && data.missingNos.length > 0) {
                    console.warn('Missing shipment IDs:', data.missingNos);
                }

                if (confirm(`Are you sure you want to delete ${tickedNos.length} shipment(s)?`)) {
                    const form = document.getElementById('shipmentTableForm');
                    if (form) {
                        const allTickedNosInput = document.getElementById('id_allTickedNos');
                        if (allTickedNosInput) {
                            allTickedNosInput.value = tickedNos.join(',');
                        }

                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'deleteShipment';
                        input.value = 'true';
                        form.appendChild(input);

                        form.submit();
                    }
                }
                isDeleting = false;
            })
            .catch(error => {
                console.error('Error fetching selections:', error);
                showMessage('Failed to retrieve selected shipments.');
                isDeleting = false;
            });
        });
    }
    
    
    // Add this helper function outside of displayExistingFiles
    function truncateFileName(fileName, maxLength = 25) {
        if (fileName.length <= maxLength) {
            return fileName;
        }
        // Truncate to maxLength, showing the start and end of the filename
        const start = fileName.substring(0, maxLength / 2);
        const end = fileName.substring(fileName.length - (maxLength / 2) + 1);
        return `${start}...${end}`;
    }

    // Function to display existing files and attach deletion logic
    function displayExistingFiles(files) {
        const pdfContainer = document.getElementById('existing_pdfs_container');
        const imageContainer = document.getElementById('existing_images_container');
        const filesToDeleteInput = document.getElementById('files_to_delete');

        // Clear previous content
        pdfContainer.innerHTML = files.filter(f => f.file_type === 'pdf').length > 0 ? '' : '<p class="text-muted m-0">No PDF files loaded.</p>';
        imageContainer.innerHTML = files.filter(f => f.file_type === 'image').length > 0 ? '' : '<p class="text-muted m-0">No Image files loaded.</p>';
        filesToDeleteInput.value = ''; // Reset the deletion list when a new shipment is loaded

        files.forEach(file => {
            const container = file.file_type === 'pdf' ? pdfContainer : imageContainer;
            const fileName = file.file.split('/').pop(); // Extract filename from URL

            const fileElement = document.createElement('div');
            fileElement.className = 'd-flex align-items-center mb-2 p-2 rounded justify-content-between border';
            fileElement.setAttribute('data-file-id', file.id);

            fileElement.innerHTML = `
                <span>
                    <i class="bi bi-${file.file_type === 'pdf' ? 'filetype-pdf' : 'image'} me-2"></i>
                    <a href="${file.file}" target="_blank">${fileName}</a>
                </span>
                <button type="button" class="btn btn-sm btn-outline-danger delete-file-btn" data-file-id="${file.id}">
                    <i class="bi bi-trash"></i> Delete
                </button>
            `;
            container.appendChild(fileElement);
        });

        // Attach deletion event listener (MUST be inside the function that generates the buttons)
        document.querySelectorAll('.delete-file-btn').forEach(button => {
            button.addEventListener('click', function() {
                const fileId = this.getAttribute('data-file-id');
                const fileDiv = document.querySelector(`div[data-file-id="${fileId}"]`);
                let filesToDelete = filesToDeleteInput.value ? filesToDeleteInput.value.split(',').filter(id => id.trim() !== '') : [];

                if (fileDiv.classList.contains('border-danger')) {
                    // UNDO Delete: Remove the ID from the list
                    fileDiv.classList.remove('border-danger', 'bg-warning-subtle');
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-outline-danger');
                    this.innerHTML = '<i class="bi bi-trash"></i> Delete';
                    filesToDelete = filesToDelete.filter(id => id !== fileId);
                } else {
                    // MARK for Delete: Add the ID to the list
                    fileDiv.classList.add('border-danger', 'bg-warning-subtle');
                    this.classList.remove('btn-outline-danger');
                    this.classList.add('btn-danger');
                    this.innerHTML = '<i class="bi bi-x-circle"></i> UNDO Delete';
                    filesToDelete.push(fileId);
                }

                // Update the hidden input value
                filesToDeleteInput.value = filesToDelete.join(',');
            });
        });
    }


    // Function to display existing files and attach deletion logic
    function displayExistingFiles(files) {
        const pdfContainer = document.getElementById('existing_pdfs_container');
        const imageContainer = document.getElementById('existing_images_container');
        const filesToDeleteInput = document.getElementById('files_to_delete');
        
        // Use a Set to track files marked for deletion locally before updating the hidden input
        let filesToDelete = new Set(
            filesToDeleteInput.value ? filesToDeleteInput.value.split(',').filter(id => id.trim() !== '') : []
        );

        // Clear previous content
        pdfContainer.innerHTML = '';
        imageContainer.innerHTML = '';

        const existingPdfs = files.filter(f => f.file_type === 'pdf');
        const existingImages = files.filter(f => f.file_type === 'image');

        // Add default messages if no files exist
        if (existingPdfs.length === 0) {
            pdfContainer.innerHTML = '<p class="text-muted m-0">No PDF files loaded.</p>';
        }
        if (existingImages.length === 0) {
            imageContainer.innerHTML = '<p class="text-muted m-0">No Image files loaded.</p>';
        }

        // Process all files
        files.forEach(file => {
            const fileId = String(file.id); // Ensure ID is a string for consistent comparison
            const container = file.file_type === 'pdf' ? pdfContainer : imageContainer;
            // Use the file_name property from your JSON response (or extract from URL if needed)
            const fullFileName = file.file_name || file.file.split('/').pop(); 
            const displayFileName = truncateFileName(fullFileName, 20); // Set max length to 20

            const isMarkedForDelete = filesToDelete.has(fileId);

            const fileElement = document.createElement('div');
            // Apply delete styling if the ID is already in the set (e.g., if re-loading data)
            fileElement.className = `d-flex align-items-center mb-2 p-2 rounded justify-content-between border ${isMarkedForDelete ? 'border-danger bg-warning-subtle' : ''}`;
            fileElement.setAttribute('data-file-id', fileId);

            const iconClass = file.file_type === 'pdf' ? 'bi-filetype-pdf text-danger' : 'bi-image text-primary';
            const btnClass = isMarkedForDelete ? 'btn-danger' : 'btn-outline-danger';
            const btnText = isMarkedForDelete ? '<i class="bi bi-x-circle"></i> UNDO Delete' : '<i class="bi bi-trash"></i> Delete';

            fileElement.innerHTML = `
                <span class="text-truncate" title="${fullFileName}">
                    <i class="bi ${iconClass} me-2"></i>
                    <a href="${file.file}" target="_blank" class="small text-decoration-none">${displayFileName}</a>
                </span>
                <button type="button" class="btn btn-sm ${btnClass} delete-file-btn flex-shrink-0" data-file-id="${fileId}">
                    ${btnText}
                </button>
            `;
            container.appendChild(fileElement);
        });
        
        // Attach event listeners after all files are rendered
        document.querySelectorAll('.delete-file-btn').forEach(button => {
            button.addEventListener('click', function() {
                const fileId = this.getAttribute('data-file-id');
                // Find the parent div element
                const fileDiv = document.querySelector(`div[data-file-id="${fileId}"]`);

                if (filesToDelete.has(fileId)) {
                    // UNDO Delete: Remove the ID from the set and reset styling
                    filesToDelete.delete(fileId);
                    fileDiv.classList.remove('border-danger', 'bg-warning-subtle');
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-outline-danger');
                    this.innerHTML = '<i class="bi bi-trash"></i> Delete';
                } else {
                    // MARK for Delete: Add the ID to the set and change styling
                    filesToDelete.add(fileId);
                    fileDiv.classList.add('border-danger', 'bg-warning-subtle');
                    this.classList.remove('btn-outline-danger');
                    this.classList.add('btn-danger');
                    this.innerHTML = '<i class="bi bi-x-circle"></i> UNDO Delete';
                }

                // Update the hidden input value (comma-separated string)
                filesToDeleteInput.value = Array.from(filesToDelete).join(',');
            });
        });
    }

    // Helper function for image modal (add this if not already present)
    function openImageModal(imageUrl) {
        // Reuse your existing imageModal or create a new one
        const modal = document.getElementById('imageModal'); // Assuming you have this modal from shipmentList_staff.html
        if (modal) {
            modal.querySelector('.modal-image').src = imageUrl;
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            // Fallback: Open in new tab
            window.open(imageUrl, '_blank');
        }
    }


    // Server-side sorting: Handle clicks on sortable headers
    document.querySelectorAll('.sortable-header').forEach(header => {
        header.addEventListener('click', function() {
            const sortKey = this.dataset.sortKey; // e.g., 'shipment_id'
            
            // Get current URL params
            const urlParams = new URLSearchParams(window.location.search);
            const currentSort = urlParams.get('sort');
            const currentOrder = urlParams.get('order') || 'asc';
            
            // Toggle order if same column, else default to 'asc'
            let newOrder = 'asc';
            if (currentSort === sortKey) {
                newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            }
            
            // Update params (preserve filters, reset page to 1)
            urlParams.set('sort', sortKey);
            urlParams.set('order', newOrder);
            urlParams.set('page', '1'); // Reset pagination on sort
            
            // Reload with new params
            window.location.search = urlParams.toString();
        });
    });

    // Handle Reset Sort button
    const resetSortBtn = document.getElementById('resetSortBtn');
    if (resetSortBtn) {
        resetSortBtn.addEventListener('click', () => {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.delete('sort');
            urlParams.delete('order');
            urlParams.set('page', '1'); // Reset to page 1
            window.location.search = urlParams.toString();
        });
    }

    const exportPdfButton = document.getElementById('exportPdfBtn');
    if (exportPdfButton) {
        exportPdfButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            // 1. Get ticked IDs
            fetch('/main1/stick_ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ action: 'get' }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.tickedNos.length === 0) {
                    showMessage('Please select at least one shipment to export.');
                    return;
                }

                // 2. Prepare Form Data
                const formData = new FormData();
                formData.append('allTickedNos', data.tickedNos.join(','));
                formData.append('exportPdfShipment', 'true');
                // We don't strictly need 'csrfmiddlewaretoken' in body if we put it in headers below, 
                // but keeping it is fine.

                // 3. FETCH THE PDF BLOB
                return fetch(window.location.href, { 
                    method: 'POST',
                    headers: {
                        // === THIS IS THE FIX ===
                        'X-CSRFToken': getCookie('csrftoken') 
                    },
                    body: formData
                });
            })
            .then(response => {
                if (!response.ok) {
                    // If we still get 403, throw an error to catch block
                    throw new Error(`Server returned ${response.status} ${response.statusText}`);
                }
                return response.blob();
            })
            .then(blob => {
                // 4. Display in Modal
                const pdfUrl = URL.createObjectURL(blob);
                const pdfIframe = document.querySelector('.modal-pdf');
                if (pdfIframe) pdfIframe.src = pdfUrl;
                
                const modal = new bootstrap.Modal(document.getElementById('pdfModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Export failed:', error);
                showMessage('Failed to generate PDF. Permissions error.');
            });
        });
    }
});