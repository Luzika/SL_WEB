const shipmentFilterForm = document.getElementById('shipmentFilterForm');

autofillToday('id_in_date_range_1');
prelistOptionCell('id_prelistCompaniesF', '#jsonDataCompaniesPrelist');
prelistOptionCell('id_divisionF', '#jsonDataDivisions');
prelistOptionCell('id_flag_statusF', '#jsonDataFlags', "ALL", "ALL");
datalistOptionCell('datalistVesselsF', '#jsonDataVessels', "");
datalistOptionCell('datalistWh', '#jsonDataWHs', "");
autofillOnVessels('id_pickVesselsF', 'id_prelistCompaniesF');
