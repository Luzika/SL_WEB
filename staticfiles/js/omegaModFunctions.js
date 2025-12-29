const omegaModForm = document.getElementById('omegaModForm');
const userIDList = document.getElementById('id_listUserID');
const MODemailCell = document.getElementById('id_MODemail');
const MODpwdCell = document.getElementById('id_MODpwd');
const MODnewPwdCell = document.getElementById('id_MODnewPwd');
const MODcompanyCell = document.getElementById('id_MODcompany');
const MODsupplierCell = document.getElementById('id_MODsupplier');
const MODisOprCell = document.getElementById('id_MODisOpr');
const MODisSplCell = document.getElementById('id_MODisSpl');
const MODisCpnCell = document.getElementById('id_MODisCpn');
const MODpermissionCell = document.getElementById('id_MODpermission');
const MODvesselsCell = document.getElementById('id_MODvesselList');


var accountList = loadJsonData('#jsonDataAccounts');
var IdList = accountList.map((item)=>item.userID);
var PwdList = accountList.map((item)=>item.password);
var EmailList = accountList.map((item)=>item.email);
var CompanyList = accountList.map((item)=>item.company);
var SupplierList = accountList.map((item)=>item.supplier);
var IsOprList = accountList.map((item)=>item.isOpr);
var IsSplList = accountList.map((item)=>item.isSpl);
var IsCpnList = accountList.map((item)=>item.isCpn);
var PermissionList = accountList.map((item)=>item.permission);
var VesselsList = accountList.map((item)=>item.vessels);

MODemailCell.readOnly = true;
MODnewPwdCell.readOnly = true;
MODnewPwdCell.placeholder = "Set new password:";
MODcompanyCell.readOnly = true;
MODsupplierCell.readOnly = true;
MODvesselsCell.readOnly = true;
MODisOprCell.disabled = true;
MODisSplCell.disabled = true;
MODisCpnCell.disabled = true;

displayAssignedPermissions();
displayAllUserIDs();
setupRoleSelectCell('id_MODisOpr', "Operator");
setupRoleSelectCell('id_MODisSpl', "Supplier");
setupRoleSelectCell('id_MODisCpn', "Company");
restrictAssignedPermissions();


function displayAssignedPermissions() {
  var permissionList = loadJsonData('#jsonDataPermissions');
  var permissionLevels = permissionList.map((item)=>item.level);
  setupPermissionSelectCell('id_MODpermission', permissionLevels);
  MODpermissionCell.selectedIndex = 0;
  MODpermissionCell.disabled = true;
}

function displayAllUserIDs() {
  setupSelectCell('id_listUserID', IdList, 
    defaltValue="", defaultOption="--------");
  
  userIDList.onchange = function() {
    fillUserInfo(userIDList, MODemailCell, EmailList, "No email yet.");
    fillUserInfo(userIDList, MODpwdCell, PwdList);
    fillUserInfo(userIDList, MODnewPwdCell, PwdList, "Set new password:");
    fillUserInfo(userIDList, MODcompanyCell, CompanyList, "No company yet.");
    fillUserInfo(userIDList, MODsupplierCell, SupplierList, "No supplier yet.");
    fillUserInfo(userIDList, MODvesselsCell, VesselsList, "No vessels yet.");
    MODpwdCell.readOnly = true;
    MODnewPwdCell.value = "";
    fillRoleInfo(userIDList, MODisOprCell, IsOprList);
    fillRoleInfo(userIDList, MODisSplCell, IsSplList);
    fillRoleInfo(userIDList, MODisCpnCell, IsCpnList);
    fillPermissionInfo(userIDList, MODpermissionCell, MODisOprCell, PermissionList);
  }
}

function fillUserInfo (userSelectCell, infoCell, dataList, placeHolder="") {
  if (userSelectCell.value === "") {
    infoCell.value = "";
    infoCell.readOnly = true;
  } else {
    let idx = IdList.indexOf(userSelectCell.value);
    infoCell.value = dataList[idx];
    infoCell.readOnly = false;
    infoCell.placeholder = placeHolder;
  }
}

function fillRoleInfo (userSelectCell, roleCell, dataList) {
  if (userSelectCell.value === "") {
    roleCell.value = "false";
    roleCell.disabled = true;
  } else {
    let idx = IdList.indexOf(userSelectCell.value);
    roleCell.value = dataList[idx];
    roleCell.disabled = false;
  }
}

function fillPermissionInfo (userSelectCell, permissionCell, oprCell, dataList) {
  permissionCell.selectedIndex = 0;
  permissionCell.disabled = true;
  if (userSelectCell.value !== "") {
    let idx = IdList.indexOf(userSelectCell.value);
    permissionCell.value = dataList[idx];
    if (oprCell.value === "true") {
      permissionCell.disabled = false;
    }
  }
}

function restrictAssignedPermissions() {
  MODisOprCell.onchange = function() {
    if (MODisOprCell.value === "false") {
      MODpermissionCell.selectedIndex = 0;
      MODpermissionCell.disabled = true;
    } else {
      MODpermissionCell.disabled = false;
    }
  }
}
