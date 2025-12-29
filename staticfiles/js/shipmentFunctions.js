function autofillToday(idCell) {
  var todayCell = document.getElementById(idCell);
  var today = new Date();
  var yyyy = today.getFullYear();
  var mm = String(today.getMonth()+1).padStart(2, '0');
  var dd = String(today.getDate()).padStart(2, '0');
  todayCell.value = yyyy + mm + dd;
}

function prelistOptionCell(idCell, dataTag,
  defaultValue="", defaultOption="----------") {
  var inputCell = document.getElementById(idCell);
  var optionList = loadJsonData(dataTag);

  var content = '';
  if (defaultValue.trim().length === 0) {
    content = '<option value="" selected="">' + defaultOption + '</option>';
  } else {
    content = '<option value=' + defaultValue + ' selected=' + defaultValue + '>';
    content += defaultOption + '</option>';
  }

  for (let i=0; i<optionList.length; i++) {
    let option = '<option value="' + optionList[i] + '">';
    option += optionList[i] + "</option>";
    content += option;
  }
  inputCell.innerHTML = content;
}

function datalistOptionCell(idCell, dataTag, defaultOption="") {
  var inputCell = document.getElementById(idCell);
  var optionList = loadJsonData(dataTag);
  let content = '<option value="" selected="">' + defaultOption + '</option>';

  for (let i=0; i<optionList.length; i++) {
    let option = '<option value="' + optionList[i] + '">';
    option += optionList[i] + "</option>";
    content += option;
  }
  inputCell.innerHTML = content;
}

function autofillOnVessels(idVesselCell, idCompanyCell,
  dataTag='#jsonDataVesselKeys') {
  var vesselSmartPick = document.getElementById(idVesselCell);
  var companyAutofill = document.getElementById(idCompanyCell);
  var vesselKeys = loadJsonData(dataTag);
  var vesselOwnedList = vesselKeys.map((item)=>item.vessel);
  var vesselOwnerList = vesselKeys.map((item)=>item.vesselOwner);

  vesselSmartPick.onchange = function() {
    let vesselPicked = vesselSmartPick.value;
    let idxPicked = vesselOwnedList.indexOf(vesselPicked);
    companyAutofill.value = vesselOwnerList[idxPicked];
  }
}

function clearAttachment(idAttachmentCell) {
  document.getElementById(idAttachmentCell).value = null;
}

function extractDate(pureDate) {
  let result = '';
  result += pureDate[0] + pureDate[1] + pureDate[2] + pureDate[3];
  result += pureDate[4] + pureDate[5] + pureDate[6] + pureDate[7];
  return result;
}

function removeItem(array, itemToRemove) {
  return array.filter(
    item => item !== itemToRemove);
}