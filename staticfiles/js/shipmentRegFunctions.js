const shipmentRegForm = document.getElementById('shipmentRegForm');
const prelistCompaniesReg = loadJsonData('#jsonDataPrelistCompanies');
const prelistSuppliersReg = loadJsonData('#jsonDataPrelistSuppliers');
const prelistDivisionsReg = loadJsonData('#jsonDataPrelistDivisions');
const prelistCPackingReg = loadJsonData('#jsonDataPrelistCPacking');
const prelistBysReg = loadJsonData('#jsonDataPrelistBys');
const datalistWarehousesReg = loadJsonData('#jsonDatalistWarehouses');
const datalistVesselsReg = loadJsonData('#jsonDatalistVessels');
const datalistCompaniesReg = loadJsonData('#jsonDataPrelistCompanies');
autofillToday('id_in_date');
setupSelectCell('id_prelistCompanies', prelistCompaniesReg);
setupSelectCell('id_division', prelistDivisionsReg);
setupSelectCell('id_by', prelistBysReg);
setupSelectCell('id_c_packing', prelistCPackingReg);
setupDatalistCell('datalistUnits', '#jsonDataPrelistUnits');
setupDatalistCell('datalistWH1', '#jsonDatalistWarehouses');
setupDatalistCell('datalistSuppliers', '#jsonDataPrelistSuppliers');
setupDatalistCell('datalistVessels', '#jsonDatalistVessels');
setupDatalistCell('datalistCompaniesReg','#jsonDataPrelistCompanies');
autofillOnVessels('id_pickVessels', 'id_prelistCompanies');


const clearPdfShipmentBtn = document.getElementById('id_clearPdf');
const clearImageShipmentBtn = document.getElementById('id_clearImage');
clearPdfShipmentBtn.onclick = function() { clearAttachment('id_pdf_file') };
clearImageShipmentBtn.onclick = function() { clearAttachment('id_image') };
