const shipmentModForm = document.getElementById('shipmentModForm');
const prelistFlagsMod = loadJsonData('#jsonDataPrelistFlags'); 
const datalistWarehousesMod = loadJsonData('#jsonDatalistWarehouses'); 

setupSelectCell('id_flag_statusM', prelistFlagsMod, "", "--------");
setupDatalistCell('datalistWhM', '#jsonDatalistWarehouses');
