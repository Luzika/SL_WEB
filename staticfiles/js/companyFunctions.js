const companyForm = document.getElementById('companyForm');
const companyList = document.getElementById('companyList');
const companyCells = companyList.getElementsByTagName('td');
const cpnListBody = document.getElementById('companyListBody');
displayAllCompanies();
clickOnCompanies();


function displayAllCompanies() {
  let content = "";
  var cpnList = loadJsonData('#jsonDataCompanies');
  var cpnIdList = cpnList.map((item)=>item.userID);
  var cpnPwdList = cpnList.map((item)=>item.password);
  var cpnEmailList = cpnList.map((item)=>item.email);
  var cpnNameList = cpnList.map((item)=>item.company);  
  var cpnVesselList = cpnList.map((item)=>item.vesselList);  
  
  let startTag = '<tr style="height: 1cm;">';
  let endTag = '</tr>';
  for (let i=0; i<cpnList.length; i++) {
    var info1 = cpnIdList[i];
    var info2 = cpnNameList[i];
    var info3 = cpnEmailList[i];
    var info4 = cpnPwdList[i];
    var info5 = cpnVesselList[i];
    let cell1 = `<td class="adminTableTd" style="width: 8%;">${info1}</td>`;
    let cell2 = `<td class="adminTableTd" style="width: 12%;">${info2}</td>`;
    let cell3 = `<td class="adminTableTd" style="width: 12%;">${info3}</td>`;
    let cell4 = `<td class="adminTableTd" style="width: 8%;">${info4}</td>`;
    let cell5 = `<td class="adminTableTd" style="width: 40%; text-align: left; padding-left: 10px;">${info5}</td>`;
    content += startTag + cell1 + cell2 + cell3 + cell4 + cell5 + endTag;
  }
  cpnListBody.innerHTML = content;
}

function clickOnCompanies() {
  let info1 = document.getElementById('id_companyID');
  let info2 = document.getElementById('id_companyName');
  let info3 = document.getElementById('id_companyEmail');  
  let info4 = document.getElementById('id_companyPwd');
  let info5 = document.getElementById('id_companyVessels');  
  
  for (let i=0; i<companyCells.length; i++) {
    let cell = companyCells[i];
    cell.onclick = function() {
      let rowId = this.parentNode.rowIndex - 1;
      let rowSelected = cpnListBody.getElementsByTagName('tr')[rowId];
      
      var infoId = rowSelected.cells[0].innerHTML;
      var infoName = rowSelected.cells[1].innerHTML;
      var infoEmail = rowSelected.cells[2].innerHTML;
      var infoPwd = rowSelected.cells[3].innerHTML;
      var infoVessels = rowSelected.cells[4].innerHTML;
      info1.value = infoId;
      info2.value = infoName;
      info3.value = infoEmail;
      info4.value = infoPwd;
      info5.value = infoVessels; 

      companyForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
      })
    }
  }
}