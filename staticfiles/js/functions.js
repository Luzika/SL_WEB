function loadJsonData(selector) {
  var dataDiv = document.querySelector(selector);
  return JSON.parse(dataDiv.getAttribute('data-json'));
}
function setTimerForRedirect(milliSeconds, targetUrl) {
  setTimeout(() => {window.location.href = targetUrl;}, milliSeconds); 
}
function autoRedirectForButton(idButton, milliSeconds) {
  let button = document.getElementById(idButton);
  setTimeout(() => {button.click();}, milliSeconds); 
}
function autofillToday(idCell) {
  var todayCell = document.getElementById(idCell);
  var today = new Date();
  var yyyy = today.getFullYear();
  var mm = String(today.getMonth()+1).padStart(2, '0');
  var dd = String(today.getDate()).padStart(2, '0');
  todayCell.value = yyyy + mm + dd;
}
function extractDate(pureDate) {
  let result = '';
  result += pureDate[0] + pureDate[1] + pureDate[2] + pureDate[3];
  result += pureDate[4] + pureDate[5] + pureDate[6] + pureDate[7];
  return result;
}
function clearAttachment(idAttachmentCell) {
  document.getElementById(idAttachmentCell).value = null;
}

function setupSelectCell(idCell, optionList, 
  defaultValue="", defaultOption="-------") {
  // Note: defaultValue=>backend; defaultOption=>frontend; 
  var inputCell = document.getElementById(idCell);
  var content = "";
  if (defaultValue.trim().length === 0) {
    content = '<option value="" selected>' + defaultOption + '</option>';
  } else {
    let defaultBE = defaultValue;
    let defaultFE = defaultOption;
    content = '<option value=' + defaultBE + ' selected=' + defaultBE + '>';
    content += defaultFE + '</option>';
  }

  // For simplicity, just assume backend and frontend display the same
  for (let i=0; i<optionList.length; i++) {
    let option = '<option value="' + optionList[i] + '">';
    option += optionList[i] + "</option>";
    content += option;
  }
  inputCell.innerHTML = content;
}

function setupChoicesCell(idCell, optionList) {
  // Note: this function is similar with the above, without default
  var inputCell = document.getElementById(idCell);
  var content = "";

  // For simplicity, just assume backend and frontend display the same
  for (let i=0; i<optionList.length; i++) {
    let option = `<option value="${optionList[i]}">${optionList[i]}</option>`;
    content += option;
  }
  inputCell.innerHTML = content;
}

function setupDatalistCell(idCell, dataTag, defaultOption="") {
  // Note: this function is similar with the above, used for datalist  
  var inputCell = document.getElementById(idCell);
  var optionList = loadJsonData(dataTag);
  let content = `<option value="" selected>${defaultOption}</option>`;

  // For simplicity, just assume backend and frontend display the same
  for (let i=0; i<optionList.length; i++) {
    let option = `<option value="${optionList[i]}">${optionList[i]}</option>`;
    content += option;
  }
  inputCell.innerHTML = content;
}


function setupRoleSelectCell(idCell, roleLabel) {
  var inputCell = document.getElementById(idCell);
  var content = "";
  let option0 = '<option value="false" selected>Not '+roleLabel + '</option>';
  let option1 = '<option value="true">Is '+roleLabel + '</option>';
  content += option0 + option1;
  inputCell.innerHTML = content;
}

function setupPermissionSelectCell(idCell, permissionLevels) {
  var inputCell = document.getElementById(idCell);
  var content = "";
  // For simplicity, just assume backend and frontend display the same
  for (let i=0; i<permissionLevels.length; i++) {
    let pmDesc = permissionLevels[i];
    let option = `<option value="${pmDesc}">${pmDesc}</option>`;
    content += option;
  }
  inputCell.innerHTML = content;
}


function autofillOnVessels(idVesselCell, idCompanyCell,
  dataTag='#jsonDatalistVesselMap') {
  var vesselSmartPick = document.getElementById(idVesselCell);
  var companyAutofill = document.getElementById(idCompanyCell);
  var vesselMap = loadJsonData(dataTag);
  var vesselOwnedList = vesselMap.map((item)=>item.vessel);
  var vesselOwnerList = vesselMap.map((item)=>item.vesselOwner);

  vesselSmartPick.onchange = function() {
    let vesselPicked = vesselSmartPick.value;
    let idxPicked = vesselOwnedList.indexOf(vesselPicked);
    companyAutofill.value = vesselOwnerList[idxPicked];
  }
}