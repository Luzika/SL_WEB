const shipmentRegFormM = document.getElementById('shipmentRegFormM');
const optionTPackingCellM = document.getElementById('id_t_packingM');
displayOptionTPackingM();


autofillToday('id_in_dateM');
prelistOptionCell('id_prelistCompaniesM', '#jsonDataCompaniesPrelist');
datalistOptionCell('datalistVesselsM', '#jsonDataVessels', "");
autofillOnVessels('id_pickVesselsM', 'id_prelistCompaniesM');


function displayOptionTPackingM() {
  var tpackingOptions = loadJsonData('#jsonDataTPacking');
  let content = '';
  for (let i=0; i<tpackingOptions.length; i++) {
    let option = '<option value="' + tpackingOptions[i] + '">';
    option += tpackingOptions[i] + "</option>";
    content += option;
  }
  optionTPackingCellM.innerHTML = content;
}