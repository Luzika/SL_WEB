const shipmentTableForm = document.getElementById('shipmentTableForm');
const statusSclicked = document.getElementById('id_statusS');
const tickedSCell = document.getElementById('id_pageSticked');
const untickedSCell = document.getElementById('id_page0Sticked');
const listStickedTotal = document.getElementById('id_listStickedTotal');
const ScheckBoxes = document.querySelectorAll('#id_selection');
checkShipmentSelection();


function checkShipmentSelection() {
  var tickedSs = tickedSCell.value.split(',');
  var untickedSs = untickedSCell.value.split(',');
  for (let i=0; i<ScheckBoxes.length; i++) {
    ScheckBoxes[i].addEventListener('change', async function() {
      if (ScheckBoxes[i].checked) {
        let idx = tickedSs.indexOf(ScheckBoxes[i].value);
        let idx0 = untickedSs.indexOf(ScheckBoxes[i].value);
        if (idx === -1) {
          tickedSs.push(ScheckBoxes[i].value);
        }
        if (idx0 > -1) {
          untickedSs.splice(idx0, 1);
        }
        tickedSCell.value = tickedSs;
        untickedSCell.value = untickedSs;
        statusSclicked.value = "ticked";
        
        const dataTableS = new FormData(shipmentTableForm);
        await fetch(shipmentTableForm.action, {
          method: shipmentTableForm.method,
          body: dataTableS,
        }).then(response => response.json());
      } else {
        let idx = untickedSs.indexOf(ScheckBoxes[i].value);
        let idx0 = tickedSs.indexOf(ScheckBoxes[i].value);
        if (idx === -1) {
          untickedSs.push(ScheckBoxes[i].value);
        }
        if (idx0 > -1) {
          tickedSs.splice(idx0, 1);
        }
        untickedSCell.value = untickedSs;
        tickedSCell.value = tickedSs;
        statusSclicked.value = "unticked";
  
        const dataTableS = new FormData(shipmentTableForm);
        await fetch(shipmentTableForm.action, {
          method: shipmentTableForm.method,
          body: dataTableS,
        }).then(response => response.json());
      }
    })
  }
}
