from django import forms
from User.models import *
from User.forms import OperatorForm, SupplierForm, CompanyForm


#=================================================================================#
#========== Split the views in the adminPage =====================================#
def user_form_view(
    request,
    form: forms.ModelForm, 
    id_field: str, 
    password_field: str,
) -> tuple[dict, forms.ModelForm]:
  result: dict = {'userTarget': None, 'adminAction': None}

  if request.method=="POST":
    username = request.POST.get(id_field, None)
    password = request.POST.get(password_field, None)
    n_targets = len(Account.objects.filter(userID=username))
    if n_targets<1:
      result['adminAction'] = "add"
    else:
      result['adminAction'] = "adjust"
      result['userTarget'] = Account.objects.get(userID=username)
  return result, form()


#=================================================================================#
#========== Handling views for operators when clicking buttons ===================#
def operator_save_request(
    request, 
    current_context: dict,
    target_role: str="operator",
    form_reload: forms.ModelForm=OperatorForm,
    form_keyword: str="operatorForm",
) -> dict:
  result = dict(current_context)
  action = current_context.get('adminAction', "add")
  form_result = form_reload(request.POST)
  if form_result.is_valid():
    if action=="add":
      form_result.save()
      form_result = form_reload()
    else:
      account = result['userTarget']
      username = request.POST.get(target_role+"ID")
      password = request.POST.get(target_role+"Pwd")
      permission = request.POST.get(target_role+"Perm")
      email = "" if not account.email else account.email
      company = "" if not account.companyName else account.companyName
      vessels = "" if not account.vesselList else account.vesselList
      modify_account(account, username, password, permission=permission, 
                      email=email, companyName=company,vesselList=vessels)
      account.isOpr = True
      account.save() 
      form_result = form_reload()
  else:
    form_result = form_reload(request.POST)
  
  result[form_keyword] = form_result
  return result

def operator_delete_request(
    request, 
    current_context: dict,
    target_role: str="operator",
    form_reload: forms.ModelForm=OperatorForm,
    form_keyword: str="operatorForm",
) -> dict:
  result = dict(current_context)
  form_result = form_reload(request.POST)
  username = request.POST.get(target_role+"ID")
  if form_result.is_valid() and username:
    account = result['userTarget']
    if account.isCpn or account.isSpl:
      account.permission = PERMISSIONS0[0]
      account_perm = assign_permission(PERMISSIONS0[0])
      account.user_permissions.clear()
      account.user_permissions.add(account_perm)
      account.isOpr = False
      account.save()
    else:
      account.delete()
  
  result[form_keyword] = form_reload()
  return result


#=================================================================================#
#========== Handling views for suppliers when clicking buttons ===================#
def supplier_save_request(
    request, 
    current_context: dict,
    target_role: str="supplier",
    form_reload: forms.ModelForm=SupplierForm,
    form_keyword: str="supplierForm",
) -> dict:
  result = dict(current_context)
  action = current_context.get('adminAction', "add")
  form_result = form_reload(request.POST)
  if form_result.is_valid():
    if action=="add":
      form_result.save()
      form_result = form_reload()
    else:
      account = result['userTarget']
      username = request.POST.get(target_role+"ID")
      password = request.POST.get(target_role+"Pwd")
      supplierName = request.POST.get(target_role+"Name")
      email = "" if not account.email else account.email
      vessels = "" if not account.vesselList else account.vesselList
      modify_account(account, username, password, email=email,
                     companyName=supplierName, vesselList=vessels)
      account.isSpl = True
      account.save() 
      form_result = form_reload()
  else:
    form_result = form_reload(request.POST)
  
  result[form_keyword] = form_result
  return result

def supplier_delete_request(
    request, 
    current_context: dict,
    target_role: str="supplier",
    form_reload: forms.ModelForm=SupplierForm,
    form_keyword: str="supplierForm",
) -> dict:
  result = dict(current_context)
  form_result = form_reload(request.POST)
  username = request.POST.get(target_role+"ID")
  if form_result.is_valid() and username:
    account = result['userTarget']
    if account.isOpr or account.isCpn:
      account.isSpl = False
      account.save()
    else:
      account.delete()
  
  result[form_keyword] = form_reload()
  return result


#=================================================================================#
#========== Handling views for companies when clicking buttons ===================#
def company_save_request(
    request, 
    current_context: dict,
    target_role: str="company",
    form_reload: forms.ModelForm=CompanyForm,
    form_keyword: str="companyForm",
) -> dict:
  result = dict(current_context)
  action = current_context.get('adminAction', "add")
  form_result = form_reload(request.POST)
  if form_result.is_valid():
    if action=="add":
      form_result.save()
      form_result = form_reload()
    else:
      account = result['userTarget']
      username = request.POST.get(target_role+"ID")
      password = request.POST.get(target_role+"Pwd")
      email = request.POST.get(target_role+"Email")
      companyName = request.POST.get(target_role+"Name")
      vessels = request.POST.get(target_role+"Vessels")
      modify_account(account, username, password, email=email,
                     companyName=companyName, vesselList=vessels)
      account.isCpn = True
      account.save() 
      form_result = form_reload()
  else:
    form_result = form_reload(request.POST)
  
  result[form_keyword] = form_result
  return result

def company_delete_request(
    request, 
    current_context: dict,
    target_role: str="company",
    form_reload: forms.ModelForm=CompanyForm,
    form_keyword: str="companyForm",
) -> dict:
  result = dict(current_context)
  form_result = form_reload(request.POST)
  username = request.POST.get(target_role+"ID")
  if form_result.is_valid() and username:
    account = result['userTarget']
    if account.isOpr or account.isSpl:
      account.isCpn = False
      account.save()
    else:
      account.delete()
  
  result[form_keyword] = form_reload()
  return result
