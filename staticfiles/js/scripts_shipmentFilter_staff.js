// Function to load JSON data from a hidden div
function loadJsonData(selector) {
  const element = document.querySelector(selector);
  if (element && element.dataset.json) {
    try {
      return JSON.parse(element.dataset.json);
    } catch (e) {
      console.error(`Error parsing JSON from ${selector}:`, e);
      return {};
    }
  }
  return {};
}

// Function to populate a <select> element
function setupSelectCell(selectId, data, defaultValue = null) {
  const selectElement = document.getElementById(selectId);
  if (selectElement && Array.isArray(data)) {
    selectElement.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = defaultValue || 'Select...';
    selectElement.appendChild(defaultOption);

    data.forEach(item => {
      const option = document.createElement('option');
      option.value = item;
      option.textContent = item;
      selectElement.appendChild(option);
    });

    const urlParams = new URLSearchParams(window.location.search);
    const paramName = selectElement.name;
    if (urlParams.has(paramName)) {
      selectElement.value = urlParams.get(paramName);
    }
  }
}

// Function to populate a <datalist> for autofill
function setupDatalistCell(inputId, dataContainerId) {
  const inputElement = document.getElementById(inputId);
  const dataContainer = document.querySelector(dataContainerId);
  if (inputElement && dataContainer && dataContainer.dataset.json) {
    const jsonData = JSON.parse(dataContainer.dataset.json);
    const datalistId = inputElement.getAttribute('list');
    const datalistElement = document.getElementById(datalistId);
    if (datalistElement) {
      datalistElement.innerHTML = '';
      jsonData.forEach(item => {
        const option = document.createElement('option');
        option.value = item;
        datalistElement.appendChild(option);
      });
    }
  }
}

// NEW FUNCTION: Autofill the company based on the selected vessel
function autofillCompanyOnVessel(vesselInputId, companySelectId, vesselMap) {
  const vesselInput = document.getElementById(vesselInputId);
  const companySelect = document.getElementById(companySelectId);

  if (vesselInput && companySelect && Object.keys(vesselMap).length > 0) {
    // Listen for the 'input' event to ensure a selection from the datalist
    vesselInput.addEventListener('input', (event) => {
      const selectedVessel = event.target.value;
      const matchingCompany = vesselMap[selectedVessel];

      if (matchingCompany) {
        console.log(`Vessel selected: ${selectedVessel}, Autoselecting company: ${matchingCompany}`);
        companySelect.value = matchingCompany;
      } else {
        console.log(`No company found for vessel: ${selectedVessel}`);
      }
    });
  }
}

// Main event listener for DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
  // === Data Loading and Autofill Setup ===
  const prelistCompaniesFil = loadJsonData('#jsonDataPrelistCompanies');
  const prelistSuppliersFil = loadJsonData('#jsonDataPrelistSuppliers');
  // const prelistDivisionsFil = loadJsonData('#jsonDataPrelistDivisions');
  // const prelistFlagsFil = loadJsonData('#jsonDataPrelistFlags');
  const datalistWarehousesFil = loadJsonData('#jsonDatalistWarehouses');
  const datalistVesselsFil = loadJsonData('#jsonDatalistVessels');
  const datalistCompaniesFil = loadJsonData('#jsonDataPrelistCompanies');

  autofillToday('id_in_date_range_1');
  setupSelectCell('id_prelistCompaniesF', prelistCompaniesFil);

  // setupSelectCell('id_divisionF', prelistDivisionsFil);
  // setupSelectCell('id_flag_statusF', prelistFlagsFil, "", "ALL");
  setupDatalistCell('datalistWhF', '#jsonDatalistWarehouses');
  setupDatalistCell('datalistSuppliersF', '#jsonDataPrelistSuppliers');
  setupDatalistCell('datalistVesselsF', '#jsonDatalistVessels');
  setupDatalistCell('datalistCompaniesFil','#jsonDataPrelistCompanies');
  autofillOnVessels('id_pickVessels', 'id_prelistCompanies');

  // === Flatpickr Date Picker Configuration ===
  const datePickerConfig = {
    dateFormat: 'Ymd',
    allowInput: true,
    onChange: function(selectedDates, dateStr, instance) {
      instance.element.value = dateStr;
    },
    onClose: function(selectedDates, dateStr, instance) {
      if (dateStr && dateStr.length === 8 && /^\d{8}$/.test(dateStr)) {
        const year = dateStr.slice(0, 4);
        const month = dateStr.slice(4, 6);
        const day = dateStr.slice(6, 8);
        const date = new Date(year, month - 1, day);
        if (date.getFullYear() != year || date.getMonth() + 1 != month || date.getDate() != day) {
          alert('Invalid date! Please enter a valid date in YYYYMMDD format.');
          instance.clear();
        }
      } else if (dateStr && dateStr.length !== 8) {
        alert('Date must be in YYYYMMDD format (8 digits)!');
        instance.clear();
      }
    }
  };

  flatpickr('#id_in_date_range_0', datePickerConfig);
  flatpickr('#id_in_date_range_1', datePickerConfig);
  flatpickr('#id_out_date_range_0', datePickerConfig);
  flatpickr('#id_out_date_range_1', datePickerConfig);

  // === Form Reset Functionality ===
  const resetBtn = document.querySelector('button[name="filterReset"]');
  if (resetBtn) {
    resetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const form = document.getElementById('shipmentFilterForm');
      if (form) {
        form.querySelectorAll('input, select').forEach(element => {
          if (element.type !== 'submit' && element.type !== 'button') {
            element.value = '';
          }
        });
        form.submit();
      }
    });
  }
  
  console.log('All form functionality initialized.');

  function setupCheckboxCell(containerId, data, paramName) {
    const container = document.getElementById(containerId);
    if (!container || !Array.isArray(data)) return;

    const urlParams = new URLSearchParams(window.location.search);
    const selectedValues = urlParams.getAll(paramName); // Gets all values for this key

    container.innerHTML = ''; // Clear existing
    data.forEach(item => {
      const wrapper = document.createElement('div');
      wrapper.className = 'form-check';
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.name = paramName;
      checkbox.value = item;
      checkbox.id = `status_${item}`;
      checkbox.className = 'form-check-input';
      
      // Keep checked if it was in the URL
      if (selectedValues.includes(item)) {
        checkbox.checked = true;
      }

      const label = document.createElement('label');
      label.htmlFor = `status_${item}`;
      label.className = 'form-check-label ms-1';
      label.textContent = item;

      wrapper.appendChild(checkbox);
      wrapper.appendChild(label);
      container.appendChild(wrapper);
    });
  }
  const flags = loadJsonData('#prelist-flags');
  setupCheckboxCell('status-checkbox-container', flags, 'flag_status');
});

