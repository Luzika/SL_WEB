from django import forms
from django.core.paginator import Paginator
from Shipment.models import *
from Shipment.forms import ShipmentRegistrationForm, ShipmentModificationForm
from datetime import datetime


RESULT_PER_PAGE = 50


#=================================================================================#
#========== Show the shipments based on the filter ===============================#
def shipment_filter_show(
    request,
    filter_reload: django_filters.FilterSet=ShipmentFilter,
) -> dict:
  shipments = Shipment.objects.all().order_by("-number")
  filter_form = filter_reload(request.GET, queryset=shipments)
  paginator = Paginator(filter_form.qs, RESULT_PER_PAGE)
  page = request.GET.get('page')
  pagination = paginator.get_page(page)

  result = {
    "shipmentFilterForm": filter_form,
    "shipmentDisplay": pagination,
    "shipmentResults": filter_form.qs,
  }
  return result


#=================================================================================#
#========== Split the views in the mainPage1 =====================================#
def shipment_form_view(
    request,
    form_reload: forms.ModelForm,
    form_keyword: str,
) -> dict:
  result: dict = {'shipmentAction': None}
  result[form_keyword] = form_reload()

  if request.method=="POST":
    if "addShipment" in request.POST:
      result['shipmentAction'] = "add"
    elif "addShipmentM" in request.POST:
      result['shipmentAction'] = "add"
    elif "adjustShipment" in request.POST:
      result['shipmentAction'] = "adjust"
    elif "modifyShipment" in request.POST:
      result['shipmentAction'] = "modify"
    elif "deleteShipment" in request.POST:
      result['shipmentAction'] = "delete"
  return result


#=================================================================================#
#========== Assume that new shipment is registered ===============================#
def shipment_register_request(
    request,
    current_context: dict,
    form_reload: forms.ModelForm=ShipmentRegistrationForm,
    form_keyword: str="shipmentRegForm",
) -> dict:
  result = dict(current_context)
  form_result = form_reload(request.POST, request.FILES)
  if form_result.is_valid():
    shipment = form_result.save()
    shipment.insert_org = request.user.userID
    shipment.work_regdate = datetime.today().strftime('%Y-%m-%d')
    shipment.save()
    form_result = form_reload()
  else:
    form_result = form_reload(request.POST, request.FILES)

  result[form_keyword] = form_result
  return result


#=================================================================================#
#========== Assume that a shipment is adjusted ===================================#
def shipment_adjust_request(
    request,
    current_context: dict,
    form_reload: forms.ModelForm=ShipmentRegistrationForm,
    form_keyword: str="shipmentRegForm",
) -> dict:
  result = dict(current_context)
  id_clicked = request.POST['clicked']
  shipment_adjusted = Shipment.objects.get(number=id_clicked)
  form_result = form_reload(request.POST, request.FILES)

  if form_result.is_valid():
    new_company = form_result.cleaned_data.get('company')
    new_vessel = form_result.cleaned_data.get('vessel')
    new_docs = form_result.cleaned_data.get('docs')
    new_odr = form_result.cleaned_data.get('odr')
    new_supplier = form_result.cleaned_data.get('supplier')
    new_division = form_result.cleaned_data.get('division')
    new_job_number = form_result.cleaned_data.get('job_number')
    new_t_packing = form_result.cleaned_data.get('t_packing')
    new_quanty = form_result.cleaned_data.get('quanty')
    new_unit = form_result.cleaned_data.get('unit')
    new_size = form_result.cleaned_data.get('size')
    new_weight = form_result.cleaned_data.get('weight')
    new_in_date = form_result.cleaned_data.get('in_date')
    new_warehouse = form_result.cleaned_data.get('warehouse')
    new_memo = form_result.cleaned_data.get('memo')
    new_by = form_result.cleaned_data.get('by')
    new_BLno = form_result.cleaned_data.get('BLno')
    new_port = form_result.cleaned_data.get('port')
    new_out_date = form_result.cleaned_data.get('out_date')
    new_remark = form_result.cleaned_data.get('remark')
    new_pdf_file = form_result.cleaned_data.get('pdf_file')
    new_image = form_result.cleaned_data.get('image')

    shipment_adjusted.company = new_company
    shipment_adjusted.vessel = new_vessel
    shipment_adjusted.docs = new_docs
    shipment_adjusted.odr = new_odr
    shipment_adjusted.supplier = new_supplier
    shipment_adjusted.division = new_division
    shipment_adjusted.job_number = new_job_number
    shipment_adjusted.t_packing = new_t_packing
    shipment_adjusted.quanty = new_quanty
    shipment_adjusted.unit = new_unit
    shipment_adjusted.size = new_size
    shipment_adjusted.weight = new_weight
    shipment_adjusted.in_date = new_in_date
    shipment_adjusted.warehouse = new_warehouse
    shipment_adjusted.memo = new_memo
    shipment_adjusted.by = new_by
    shipment_adjusted.BLno = new_BLno
    shipment_adjusted.port = new_port
    shipment_adjusted.out_date = new_out_date
    shipment_adjusted.remark = new_remark
    shipment_adjusted.pdf_file = new_pdf_file
    shipment_adjusted.image = new_image

    shipment_adjusted.correct_org = request.user.userID
    shipment_adjusted.save()
    form_result = form_reload()
  else:
    form_result = form_reload(request.POST, request.FILES)

  result[form_keyword] = form_result
  return result


#=================================================================================#
#========== Assume that many shipments are modified (or deleted) =================#
def shipment_modify_request(
    request,
    current_context: dict,
    form_reload: forms.ModelForm=ShipmentModificationForm,
    form_keyword: str="shipmentModForm",
) -> dict:
  result = dict(current_context)
  if request.POST['ticked'] == "":
    return result

  list_id_ticked = request.POST['ticked'].split(',')
  list_id_ticked = [Id for Id in list_id_ticked if Id]

  if result['shipmentAction']=="modify":
    form_result = form_reload(request.POST)
    if form_result.is_valid():
      mod_in_date = form_result.cleaned_data.get('in_dateM')
      mod_out_date = form_result.cleaned_data.get('out_dateM')
      mod_job_number = form_result.cleaned_data.get('job_numberM')
      mod_port = form_result.cleaned_data.get('portM')
      mod_flag_status = form_result.cleaned_data.get('flag_statusM')
      mod_remark = form_result.cleaned_data.get('remarkM')
      mod_memo = form_result.cleaned_data.get('memoM')
      mod_warehouse = form_result.cleaned_data.get('warehouseM')

      for id_ticked in list_id_ticked:
        id_ticked = int(id_ticked)
        n_checkticked = len(Shipment.objects.filter(number=id_ticked))
        if n_checkticked < 1:
          continue
        shipment_modified = Shipment.objects.get(number=id_ticked)
        if mod_in_date:
          shipment_modified.in_date = mod_in_date
        if mod_out_date:
          shipment_modified.out_date = mod_out_date
        if mod_job_number:
          shipment_modified.job_number = mod_job_number
        if mod_port:
          shipment_modified.port = mod_port
        if mod_in_date:
          shipment_modified.in_date = mod_in_date
        if mod_flag_status:
          shipment_modified.flag_status = mod_flag_status
        if mod_remark:
          shipment_modified.remark = mod_remark
        if mod_memo:
          shipment_modified.memo = mod_memo
        if mod_warehouse:
          shipment_modified.warehouse = mod_warehouse

        shipment_modified.correct_org = request.user.userID
        shipment_modified.save()
      form_result = form_reload()
    else:
      form_result = form_reload(request.POST)

  elif result['shipmentAction']=="delete":
    for id_ticked in list_id_ticked:
      id_ticked = int(id_ticked)
      n_checkticked = len(Shipment.objects.filter(number=id_ticked))
      if n_checkticked < 1:
        continue
      shipment_modified = Shipment.objects.get(number=id_ticked)
      shipment_modified.delete()
    form_result = form_reload()

  result[form_keyword] = form_result
  return result
