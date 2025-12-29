function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

const debouncedUpdateTickedNos = debounce((tickedNos, untickedNos) => {
  console.log(`Updating tickedNos: ${tickedNos.length} items`, tickedNos);
  console.log(`Updating untickedNos: ${untickedNos.length} items`, untickedNos);
  fetch('/main1/pageSelect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ tickedNos, untickedNos, action: 'update' }),
  }).then(response => {
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return response.json();
  }).then(data => {
    console.log(`Server confirmed ${data.tickedNos.length} tickedNos`, data.tickedNos);
    tickedSCell.value = data.tickedNos.join(',');
    ticked1SCell.value = tickedSCell.value;
    untickedSCell.value = untickedNos.join(',');
    document.getElementById('totalTicked').textContent = data.tickedNos.length;
  }).catch(error => {
    console.error('Fetch error:', error);
  });
}, 300);

const shipmentTableForm = document.getElementById('shipmentTableForm');
const shipmentTable = document.getElementById('shipmentTable');
const shipmentCellClicked = document.getElementById('id_clicked');
const statusSclicked = document.getElementById('id_statusS');
const tickedSCell = document.getElementById('id_pageSticked');
const ticked1SCell = document.getElementById('id_page1Sticked');
const untickedSCell = document.getElementById('id_page0Sticked');
const pageSelect = document.getElementById('pageSelect');
const ScheckallBoxes = document.getElementById('id_selectall');

function getCheckboxes() {
  const checkboxes = document.querySelectorAll('#shipmentTableForm input[name="selection"]');
  console.log(`Found ${checkboxes.length} checkboxes`);
  return Array.from(checkboxes);
}

function checkShipmentSelection() {
  const tickedSs = tickedSCell.value ? tickedSCell.value.split(',').filter(id => id) : [];
  const untickedSs = untickedSCell.value ? untickedSCell.value.split(',').filter(id => id) : [];
  const checkboxes = getCheckboxes();

  checkboxes.forEach(cb => {
    cb.addEventListener('change', function() {
      const value = cb.value;
      if (cb.checked) {
        if (!tickedSs.includes(value)) tickedSs.push(value);
        const idx0 = untickedSs.indexOf(value);
        if (idx0 > -1) untickedSs.splice(idx0, 1);
        statusSclicked.value = "ticked";
      } else {
        if (!untickedSs.includes(value)) untickedSs.push(value);
        const idx0 = tickedSs.indexOf(value);
        if (idx0 > -1) tickedSs.splice(idx0, 1);
        statusSclicked.value = "unticked";
      }
      debouncedUpdateTickedNos(tickedSs, untickedSs);
    });
    cb.checked = tickedSs.includes(cb.value);
  });
}

function checkallShipmentSelection() {
  if (ScheckallBoxes) {
    ScheckallBoxes.addEventListener('change', function() {
      const checkboxes = getCheckboxes();
      checkboxes.forEach(cb => cb.checked = ScheckallBoxes.checked);
      const tickedSs = ScheckallBoxes.checked ? checkboxes.map(cb => cb.value) : [];
      const untickedSs = ScheckallBoxes.checked ? [] : checkboxes.map(cb => cb.value);
      debouncedUpdateTickedNos(tickedSs, untickedSs);
    });
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function singleClickOnShipments() {
  const shipmentCells = shipmentTable.getElementsByTagName('td');
  const shipmentInfo1 = document.getElementById('id_prelistCompanies');
  const shipmentInfo2 = document.getElementById('id_pickVessels');
  const shipmentInfo3 = document.getElementById('id_docs');
  const shipmentInfo4 = document.getElementById('id_POno');
  const shipmentInfo5 = document.getElementById('id_supplier');
  const shipmentInfo6 = document.getElementById('id_division');
  const shipmentInfo7 = document.getElementById('id_job_number');
  const shipmentInfo8 = document.getElementById('id_c_packing');
  const shipmentInfo9 = document.getElementById('id_quanty');
  const shipmentInfo10 = document.getElementById('id_pickUnits');
  const shipmentInfo11 = document.getElementById('id_size');
  const shipmentInfo12 = document.getElementById('id_weight');
  const shipmentInfo13 = document.getElementById('id_division');
  const shipmentInfo14 = document.getElementById('id_in_date');
  const shipmentInfo15 = document.getElementById('id_pickWH1');
  const shipmentInfo16 = document.getElementById('id_memo');
  const shipmentInfo17 = document.getElementById('id_by');
  const shipmentInfo18 = document.getElementById('id_BLno');
  const shipmentInfo19 = document.getElementById('id_port');
  const shipmentInfo20 = document.getElementById('id_out_date');
  const shipmentInfo21 = document.getElementById('id_remark');

  for (let i = 0; i < shipmentCells.length; i++) {
    let cell = shipmentCells[i];
    cell.onclick = function(e) {
      // Prevent form population if clicking the Shipment ID link
      if (e.target.closest('.shipment-id-link')) {
        return; // Let the link navigate to tracking page
      }

      let rowId = this.parentNode.rowIndex;
      let rowSelected = shipmentTable.getElementsByTagName('tr')[rowId];
      shipmentCellClicked.value = rowSelected.cells[0].firstElementChild.value;
      let pivotCell1 = rowSelected.cells[1]; // Shipment ID
      let pivotCell2 = rowSelected.cells[2]; // Company

      if (cell === pivotCell1 || cell === pivotCell2) {
        let dataCompany = rowSelected.cells[2].innerText; // Company
        let dataVessel = rowSelected.cells[3].innerText;  // Vessel
        let dataDocs = rowSelected.cells[4].innerText;    // Doc
        let dataPOno = rowSelected.cells[6].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Po.No
        let dataSupplier = rowSelected.cells[7].innerText; // Supplier
        let dataCPacking = rowSelected.cells[8].innerText; // C.Packing
        let dataQuanty = rowSelected.cells[9].innerText;   // Qty
        let dataUnit = rowSelected.cells[10].innerText;    // Unit
        let dataSize = rowSelected.cells[11].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Size
        let dataWeight = rowSelected.cells[12].innerText;  // Weight
        let dataDivision = rowSelected.cells[13].innerText; // Division (hidden)
        let dataInDate = rowSelected.cells[14].innerText;  // In
        let dataWh = rowSelected.cells[15].innerText;      // W/H
        let dataBy = rowSelected.cells[16].innerText;      // By
        let dataBLno = rowSelected.cells[17].innerText;    // BLNO
        let dataPort = rowSelected.cells[18].innerText;    // Port
        let dataOutDate = rowSelected.cells[19].innerText; // Onboard Date
        let dataRemark = rowSelected.cells[20].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Remark
        let dataMemo = rowSelected.cells[21].innerText;    // Memo
        let dataJobNo = rowSelected.cells[22].innerText;   // Job No

        dataInDate = String(dataInDate.trim());
        dataOutDate = String(dataOutDate.trim());

        shipmentInfo1.value = dataCompany;
        shipmentInfo2.value = dataVessel;
        shipmentInfo3.value = dataDocs;
        shipmentInfo4.value = dataPOno;
        shipmentInfo5.value = dataSupplier;
        shipmentInfo6.value = dataDivision;
        shipmentInfo7.value = dataJobNo;
        shipmentInfo8.value = dataCPacking;
        shipmentInfo9.value = dataQuanty;
        shipmentInfo10.value = dataUnit;
        shipmentInfo11.value = dataSize;
        shipmentInfo12.value = dataWeight;
        shipmentInfo13.value = dataDivision.trim();
        shipmentInfo14.value = extractDate(dataInDate);
        shipmentInfo15.value = dataWh;
        shipmentInfo16.value = dataMemo;
        shipmentInfo17.value = dataBy;
        shipmentInfo18.value = dataBLno;
        shipmentInfo19.value = dataPort;
        shipmentInfo20.value = dataOutDate.length ? extractDate(dataOutDate) : '';
        shipmentInfo21.value = dataRemark;
        shipmentRegForm.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }
    };
  }
}

document.addEventListener('DOMContentLoaded', () => {
  checkShipmentSelection();
  checkallShipmentSelection();
  singleClickOnShipments();
});