const omegaRegForm = document.getElementById('omegaRegForm');
const REGisOprCell = document.getElementById('id_isOpr');
const REGisSplCell = document.getElementById('id_isSpl');
const REGisCpnCell = document.getElementById('id_isCpn');
const REGpermissionCell = document.getElementById('id_permission');
setupRoleSelectCell('id_isOpr', "Operator");
setupRoleSelectCell('id_isSpl', "Supplier");
setupRoleSelectCell('id_isCpn', "Company");
displayAllPermissions();
restrictPermissions();


function displayAllPermissions() {
  var permissionList = loadJsonData('#jsonDataPermissions');
  var permissionLevels = permissionList.map((item)=>item.level);
  setupPermissionSelectCell('id_permission', permissionLevels);
  REGpermissionCell.selectedIndex = 0;
  REGpermissionCell.disabled = true;
}

function restrictPermissions() {
  REGisOprCell.onchange = function() {
    if (REGisOprCell.value === "false") {
      REGpermissionCell.selectedIndex = 0;
      REGpermissionCell.disabled = true;
    } else {
      REGpermissionCell.disabled = false;
    }
  }
}
