const shipmentTable = document.getElementById('shipmentTable');
const shipmentCells = shipmentTable.getElementsByTagName('td');
const shipmentCheckboxes = shipmentTable.getElementsByTagName('input');
const shipmentClicked = document.getElementById('id_clicked');
const shipmentTicked = document.getElementById('id_ticked');
var shipmentList = loadJsonData('#jsonDataShipments');
var shipmentsTicked = [];

var shipmentInfo1 = document.getElementById('id_prelistCompanies');
var shipmentInfo2 = document.getElementById('id_pickVessels');
var shipmentInfo3 = document.getElementById('id_docs');
var shipmentInfo4 = document.getElementById('id_odr');
var shipmentInfo5 = document.getElementById('id_supplier');
var shipmentInfo6 = document.getElementById('id_division');
var shipmentInfo7 = document.getElementById('id_job_number');
var shipmentInfo8 = document.getElementById('id_t_packing');
var shipmentInfo9 = document.getElementById('id_quanty');
var shipmentInfo10 = document.getElementById('id_pickUnits');
var shipmentInfo11 = document.getElementById('id_size');
var shipmentInfo12 = document.getElementById('id_weight');
var shipmentInfo13 = document.getElementById('id_in_date');
var shipmentInfo14 = document.getElementById('id_pickWH1');
var shipmentInfo15 = document.getElementById('id_memo');
var shipmentInfo16 = document.getElementById('id_by');
var shipmentInfo17 = document.getElementById('id_BLno');
var shipmentInfo18 = document.getElementById('id_port');
var shipmentInfo19 = document.getElementById('id_out_date');
var shipmentInfo20 = document.getElementById('id_remark');
clickOnShipments();
tickOnShipments();


function clickOnShipments() {
  for (let i=0; i<shipmentCells.length; i++) {
    let cell = shipmentCells[i];
    cell.onclick = function() {
      let rowId = this.parentNode.rowIndex;
      let rowSelected = shipmentTable.getElementsByTagName('tr')[rowId];
      var shipmentId = rowSelected.cells[0].firstElementChild.value;
      shipmentClicked.value = shipmentId;
      
      let dataCompany = rowSelected.cells[1].innerHTML;
      let dataVessel = rowSelected.cells[2].innerHTML;
      let dataDocs = rowSelected.cells[3].innerHTML;
      let dataOdr = rowSelected.cells[4].innerHTML;
      let dataSupplier = rowSelected.cells[5].innerHTML;
      let dataTPacking = rowSelected.cells[6].innerHTML;
      let dataQuanty = rowSelected.cells[7].innerHTML;
      let dataUnit = rowSelected.cells[8].innerHTML;
      let dataSize = rowSelected.cells[9].innerHTML;
      let dataWeight = rowSelected.cells[10].innerHTML;
      let dataDivision = rowSelected.cells[11].innerHTML;
      let dataInDate = rowSelected.cells[12].innerHTML;
      let dataWh = rowSelected.cells[13].innerHTML;
      let dataBy = rowSelected.cells[14].innerHTML;
      let dataBLno = rowSelected.cells[15].innerHTML;
      let dataPort = rowSelected.cells[16].innerHTML;
      let dataOutDate = rowSelected.cells[17].innerHTML;
      let dataRemark = rowSelected.cells[18].innerHTML;
      let dataMemo = rowSelected.cells[19].innerHTML;
      let dataJobNo = rowSelected.cells[20].innerHTML;
      dataInDate = String(dataInDate.trim());
      dataOutDate = String(dataOutDate.trim());

      shipmentInfo1.value = dataCompany;
      shipmentInfo2.value = dataVessel;
      shipmentInfo3.value = dataDocs;
      shipmentInfo4.value = dataOdr;
      shipmentInfo5.value = dataSupplier;
      shipmentInfo6.value = dataDivision;
      shipmentInfo7.value = dataJobNo;
      shipmentInfo8.value = dataTPacking;
      shipmentInfo9.value = dataQuanty;
      shipmentInfo10.value = dataUnit;
      shipmentInfo11.value = dataSize;
      shipmentInfo12.value = dataWeight;
      shipmentInfo13.value = extractDate(dataInDate);
      shipmentInfo14.value = dataWh;
      shipmentInfo15.value = dataMemo;
      shipmentInfo16.value = dataBy;
      shipmentInfo17.value = dataBLno;
      shipmentInfo18.value = dataPort;
      if (dataOutDate.length === 0) {
        shipmentInfo19.value = "";  
      } else {
        shipmentInfo19.value = extractDate(dataOutDate);
      }
      shipmentInfo20.value = dataRemark;
      
      if (cell.cellIndex == 1 | cell.cellIndex == 2) {
        window.scrollTo({top: 0, behavior: 'smooth'});
      }
    }
  }
}

function tickOnShipments() {
  for (let i=1; i<shipmentCheckboxes.length; i++) {
    shipmentCheckboxes[i].value;
    shipmentCheckboxes[i].addEventListener('change', function() 
    {
      var idx = shipmentsTicked.indexOf(shipmentCheckboxes[i].value);        
      if (shipmentCheckboxes[i].checked && idx == -1) {
        shipmentsTicked.push(shipmentCheckboxes[i].value);
      } 
      if (!shipmentCheckboxes[i].checked && idx !== -1) {
        shipmentsTicked.splice(idx, 1);
      };
      tickedValues = shipmentsTicked;
      tickedValues.sort(function(a, b) { return b - a });
      shipmentTicked.value = tickedValues;
    });
  }
}
shipmentCheckboxes[0].addEventListener('change', function() 
{
  for (let i=1; i<shipmentCheckboxes.length; i++) {
    shipmentCheckboxes[i].checked = this.checked;
    var idx = shipmentsTicked.indexOf(shipmentCheckboxes[i].value);        
    if (shipmentCheckboxes[i].checked && idx == -1) {
      shipmentsTicked.push(shipmentCheckboxes[i].value);
    } 
    if (!shipmentCheckboxes[i].checked && idx !== -1) {
      shipmentsTicked.splice(idx, 1);
    };
    tickedValues = shipmentsTicked;
    tickedValues.sort(function(a, b) { return b - a });
    shipmentTicked.value = tickedValues;
  };
});
