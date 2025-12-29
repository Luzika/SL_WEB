const operatorForm = document.getElementById('operatorForm');
const operatorList = document.getElementById('operatorList');
const operatorCells = operatorList.getElementsByTagName('td');
const oprListBody = document.getElementById('operatorListBody');
const OPRpermissionCell = document.getElementById('id_operatorPerm');
displayOprPermissions();
displayAllOperators();
clickOnOperators();


function displayOprPermissions() {
  var permissionList = loadJsonData('#jsonDataPermissions');
  var permissionLevels = permissionList.map((item)=>item.level);
  setupPermissionSelectCell('id_operatorPerm', permissionLevels);
}

function displayAllOperators() {
  let content = "";
  var oprList = loadJsonData('#jsonDataOperators');
  var oprIdList = oprList.map((item)=>item.userID);
  var oprPwdList = oprList.map((item)=>item.password);
  var oprPermList = oprList.map((item)=>item.permission);
  
  let startTag = '<tr style="height: 1cm;">';
  let endTag = '</tr>';
  for (let i=0; i<oprList.length; i++) {
    var info1 = oprIdList[i];
    var info2 = oprPwdList[i];
    var info3 = oprPermList[i];
    let cell1 = `<td class="adminTableTd" style="width: 24%;">${info1}</td>`;
    let cell2 = `<td class="adminTableTd" style="width: 32%;">${info2}</td>`;
    let cell3 = '<td class="adminTableTd" ';
    if (info3 === "Read + Modify") {
      cell3 += `style="color: red; width: 24%;">${info3}</td>`
    } else {
      cell3 += `style="color: gray; width: 24%;">${info3}</td>`
    }
    content += startTag + cell1 + cell2 + cell3 + endTag;
  }
  oprListBody.innerHTML = content;
}

function clickOnOperators() {
  let info1 = document.getElementById('id_operatorID');
  let info2 = document.getElementById('id_operatorPwd');
  let info3 = document.getElementById('id_operatorPerm');  
  
  for (let i=0; i<operatorCells.length; i++) {
    let cell = operatorCells[i];
    cell.onclick = function() {
      let rowId = this.parentNode.rowIndex - 1;
      let rowSelected = oprListBody.getElementsByTagName('tr')[rowId];
      
      var infoId = rowSelected.cells[0].innerHTML;
      var infoPwd = rowSelected.cells[1].innerHTML;
      var infoPerm = rowSelected.cells[2].innerHTML;
      info1.value = infoId;
      info2.value = infoPwd;
      info3.value = infoPerm;
      
      operatorForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
      })
    }
  }
}