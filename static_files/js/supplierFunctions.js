const supplierForm = document.getElementById('supplierForm');
const supplierList = document.getElementById('supplierList');
const supplierCells = supplierList.getElementsByTagName('td');
const splListBody = document.getElementById('supplierListBody');
displayAllSuppliers();
clickOnSuppliers();


function displayAllSuppliers() {
  let content = "";
  var splList = loadJsonData('#jsonDataSuppliers');
  var splIdList = splList.map((item)=>item.userID);
  var splPwdList = splList.map((item)=>item.password);
  var splNameList = splList.map((item)=>item.supplier);
  
  let startTag = '<tr style="height: 1cm;">';
  let endTag = '</tr>';
  for (let i=0; i<splList.length; i++) {
    var info1 = splIdList[i];
    var info2 = splNameList[i];
    var info3 = splPwdList[i];
    let cell1 = `<td class="adminTableTd" style="width: 24%;">${info1}</td>`;
    let cell2 = `<td class="adminTableTd" style="width: 32%;">${info2}</td>`;
    let cell3 = `<td class="adminTableTd" style="width: 24%;">${info3}</td>`;
    content += startTag + cell1 + cell2 + cell3 + endTag;
  }
  splListBody.innerHTML = content;
}

function clickOnSuppliers() {
  let info1 = document.getElementById('id_supplierID');
  let info2 = document.getElementById('id_supplierName');
  let info3 = document.getElementById('id_supplierPwd');  
  
  for (let i=0; i<supplierCells.length; i++) {
    let cell = supplierCells[i];
    cell.onclick = function() {
      let rowId = this.parentNode.rowIndex - 1;
      let rowSelected = splListBody.getElementsByTagName('tr')[rowId];
      
      var infoId = rowSelected.cells[0].innerHTML;
      var infoName = rowSelected.cells[1].innerHTML;
      var infoPwd = rowSelected.cells[2].innerHTML;
      info1.value = infoId;
      info2.value = infoName;
      info3.value = infoPwd;
      
      supplierForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
      })
    }
  }
}