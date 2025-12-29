const omegaTableU = document.getElementById('omegaTableU');
// const firstPageUlink = document.getElementById('id_firstPageU');
// const prevPageUlink = document.getElementById('id_prevPageU');
// const nextPageUlink = document.getElementById('id_nextPageU');
// const lastPageUlink = document.getElementById('id_lastPageU');
const statusUclicked = document.getElementById('id_status');
const tickedUCell = document.getElementById('id_pageUticked');
const untickedUCell = document.getElementById('id_page0Uticked');
// const listUtickedCell = document.getElementById('id_listUticked');
// const list0UtickedCell = document.getElementById('id_list0Uticked');
const listUtickedTotal = document.getElementById('id_listUtickedTotal');
const UcheckBoxes = document.querySelectorAll('#id_Utick');

var tickedUs = tickedUCell.value.split(',');
var untickedUs = untickedUCell.value.split(',');
// var listUs = listUtickedCell.value.split(',');
// var list0Us = list0UtickedCell.value.split(',');
// var listUtotal = listUtickedTotal.value.split(',');
// alert(listUtickedTotal.value);
for (let i=0; i<UcheckBoxes.length; i++) {
  UcheckBoxes[i].addEventListener('change', async function() {
    if (UcheckBoxes[i].checked) {
      let idx = tickedUs.indexOf(UcheckBoxes[i].value);
      let idx0 = untickedUs.indexOf(UcheckBoxes[i].value);
      if (idx === -1) {
        tickedUs.push(UcheckBoxes[i].value);
      }
      if (idx0 > -1) {
        untickedUs.splice(idx0, 1);
      }
      tickedUCell.value = tickedUs;
      untickedUCell.value = untickedUs;
      statusUclicked.value = "ticked";
      
      const dataTableU = new FormData(omegaTableU);
      await fetch(omegaTableU.action, {
        method: omegaTableU.method,
        body: dataTableU,
      }).then(response => response.json());
    } else {
      let idx = untickedUs.indexOf(UcheckBoxes[i].value);
      let idx0 = tickedUs.indexOf(UcheckBoxes[i].value);
      if (idx === -1) {
        untickedUs.push(UcheckBoxes[i].value);
      }
      if (idx0 > -1) {
        tickedUs.splice(idx0, 1);
      }
      untickedUCell.value = untickedUs;
      tickedUCell.value = tickedUs;
      statusUclicked.value = "unticked";

      const dataTableU = new FormData(omegaTableU);
      await fetch(omegaTableU.action, {
        method: omegaTableU.method,
        body: dataTableU,
      }).then(response => response.json());
    }
  })
}