const shipmentFilterForm = document.getElementById('shipmentFilterForm');
const prelistCompaniesFil = loadJsonData('#jsonDataPrelistCompanies');
const prelistSuppliersFil = loadJsonData('#jsonDataPrelistSuppliers');
const prelistDivisionsFil = loadJsonData('#jsonDataPrelistDivisions');
const prelistFlagsFil = loadJsonData('#jsonDataPrelistFlags');
const datalistWarehousesFil = loadJsonData('#jsonDatalistWarehouses');
const datalistVesselsFil = loadJsonData('#jsonDatalistVessels');
const datalistCompaniesFil = loadJsonData('#jsonDataPrelistCompanies');

autofillToday('id_in_date_range_1');
setupSelectCell('id_prelistCompaniesF', prelistCompaniesFil);

setupSelectCell('id_divisionF', prelistDivisionsFil);
setupSelectCell('id_flag_statusF', prelistFlagsFil, "", "ALL");
setupDatalistCell('datalistWhF', '#jsonDatalistWarehouses');
setupDatalistCell('datalistSuppliersF', '#jsonDataPrelistSuppliers');
setupDatalistCell('datalistVesselsF', '#jsonDatalistVessels');
setupDatalistCell('datalistCompaniesFil','#jsonDataPrelistCompanies');
autofillOnVessels('id_pickVesselsF', 'id_prelistCompaniesF');
