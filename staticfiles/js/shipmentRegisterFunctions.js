const shipmentRegForm = document.getElementById('shipmentRegForm');
const optionTPackingCell = document.getElementById('id_t_packing');
const clearPdfShipmentBtn = document.getElementById('id_clearPdf');
const clearImageShipmentBtn = document.getElementById('id_clearImage');
clearPdfShipmentBtn.onclick = function() { clearAttachment('id_pdf_file') };
clearImageShipmentBtn.onclick = function() { clearAttachment('id_image') };
displayOptionTPacking();


autofillToday('id_in_date');
prelistOptionCell('id_prelistCompanies', '#jsonDataCompaniesPrelist');
prelistOptionCell('id_division', '#jsonDataDivisions');
// prelistOptionCell('id_t_packing', '#jsonDataTPacking');
prelistOptionCell('id_by', '#jsonDataBys');
datalistOptionCell('datalistVessels', '#jsonDataVessels', "");
datalistOptionCell('datalistWH1', '#jsonDataWHs', "");
datalistOptionCell('datalistUnits', '#jsonDataUnits', "");
autofillOnVessels('id_pickVessels', 'id_prelistCompanies');


function displayOptionTPacking() {
  var tpackingOptions = loadJsonData('#jsonDataTPacking');
  let content = '';
  for (let i=0; i<tpackingOptions.length; i++) {
    let option = '<option value="' + tpackingOptions[i] + '">';
    option += tpackingOptions[i] + "</option>";
    content += option;
  }
  optionTPackingCell.innerHTML = content;
}
