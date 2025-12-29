// === The singleclickfunction.js file is intentionally left empty. === //
function singleClickFunction() {
    // This function is a placeholder for single-click actions.
    const shipmentCells = shipmentTable.getElementsByTagName('td');
    const ship_info_company = document.getElementById('id_prelistCompanies');
    const ship_info_vessel = document.getElementById('id_pickVessels');
    const ship_info_supplier = document.getElementById('id_supplier');
    const ship_info_IMP = document.getElementById('id_IMP_BL');
    const ship_info_EXP = document.getElementById('id_EXP_BL');
    const ship_info_orderNo = document.getElementById('id_Order_No');

    const ship_info_division = document.getElementById('id_division');
    const ship_info_quantity = document.getElementById('id_quanty');
    const ship_info_weight = document.getElementById('id_weight');
    const ship_info_cpacking = document.getElementById('id_c_packing');
    const ship_info_units = document.getElementById('id_pickUnits');
    const ship_info_size = document.getElementById('id_size');
    const ship_info_docs = document.getElementById('id_docs');

    const ship_info_indate = document.getElementById('id_in_date');
    const ship_info_warehouse = document.getElementById('id_pickWH1');
    const ship_info_by = document.getElementById('id_by');
    const ship_info_port = document.getElementById('id_port');
    const ship_info_onboarddate = document.getElementById('id_out_date');
    const ship_info_remarks = document.getElementById('id_remark');

    for (let i = 0; i < shipmentCells.length; i++) {
        let cell = shipmentCells[i];
        cell.onclick = function(e) {
        // Prevent form population if clicking the Shipment ID link
        if (e.target.closest('.shipment-id-link')) {
            return; // Let the link navigate to tracking page
        }

        let rowID = this.parentNode.rowIndex;
        let rowSelected = shipmentTable.getElementsByTagName('tr')[rowID];
        shipmentCellClicked.value = rowSelected.cells[0].firstElementChild.value;
        let pivotCell2 = rowSelected.cells[2]; // Company
        let pivotCell3 = rowSelected.cells[3]; // Vessel

        if (cell === pivotCell2 || cell === pivotCell3) {
            let company = rowSelected.cells[2].innerText;
            let vessel = rowSelected.cells[3].innerText;
            let doc = rowSelected.cells[4].innerText;
            let orderNo = rowSelected.cells[5].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Po.No change to Order No
            let supplier = rowSelected.cells[6].innerText;
            let Cpacking = rowSelected.cells[7].innerText;
            let quantity = rowSelected.cells[8].innerText;
            let unit = rowSelected.cells[9].innerText;
            let size = rowSelected.cells[10].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Size
            let weight = rowSelected.cells[11].innerText;
            let division = rowSelected.cells[12].innerText;
            let indate = rowSelected.cells[13].innerText;
            let warehouse = rowSelected.cells[14].innerText;
            let by = rowSelected.cells[15].innerText;
            let imp_bl = rowSelected.cells[16].innerText;
            let port = rowSelected.cells[17].innerText;
            let onboarddate = rowSelected.cells[18].innerText;
            let remark = rowSelected.cells[18].innerHTML.replace(/<br\s*\/?>/gi, '\n').trim(); // Remark
            let exp_bl = rowSelected.cells[19].innerText;

            indate = String(indate.trim());
            onboarddate = String(onboarddate.trim());

            ship_info_company.value = company;
            ship_info_vessel.value = vessel;
            ship_info_supplier.value = supplier;
            ship_info_IMP.value = imp_bl;
            ship_info_EXP.value = exp_bl;
            ship_info_orderNo.value = orderNo;
            ship_info_division.value = division.trim();;
            ship_info_quantity.value = quantity;
            ship_info_weight.value = weight;
            ship_info_cpacking.value = Cpacking;
            ship_info_units.value = unit;
            ship_info_size.value = size;
            ship_info_docs.value = doc;
            ship_info_indate.value = extractDate(indate);;
            ship_info_warehouse.value = warehouse;
            ship_info_by.value = by;
            ship_info_port.value = port;
            ship_info_onboarddate.value = onboarddate.length ? extractDate(onboarddate) : '';
            ship_info_remarks.value = remark;
            shipmentRegForm.scrollIntoView({
            behavior: "smooth",
            block: "start"
            });
        }
        };
    }
}