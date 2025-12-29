from django import forms
from User.models import *
from User.forms import OperatorForm, SupplierForm, CompanyForm


ADMIN_PROCESS_DICT = {
  "operator": {
    "form": OperatorForm,
    "form_keyword": "operatorForm",
    "button_keywords": ["saveOperator", "deleteOperator"],
    "id_keyword": "operatorID",
  },
  "supplier": {
    "form": SupplierForm,
    "form_keyword": "supplierForm",
    "button_keywords": ["saveSupplier", "deleteSupplier"],
    "id_keyword": "supplierID",
  },
  "company": {
    "form": CompanyForm,
    "form_keyword": "companyForm",
    "button_keywords": ["saveCompany", "deleteCompany"],
    "id_keyword": "companyID",
  }
}


#=================================================================================#
#========== General format to handle a request in adminPage (POST/GET) ===========#
def setup_admin_request(
    request,
    process_dict: dict,
) -> dict:
  form = process_dict["form"]
  form_keyword = process_dict["form_keyword"]
  button_keywords = process_dict["button_keywords"]
  id_keyword = process_dict["id_keyword"]
  
  result = {form_keyword: form(), "_post": False}
  if request.method == "POST":
    for button in button_keywords:
      if button not in request.POST:
        continue
      
      form_result = form(request.POST)
      result["_clicked"] = button
      result["_post"] = True
      if form_result.is_valid():
        result["_username"] = form_result.cleaned_data.get(id_keyword)
      else:
        form_result = form(request.POST)
      result[form_keyword] = form_result
  return result
#=================================================================================#

#=================================================================================#
#========== Specific actions for Operators: register/update/delete ===============#
def update_operator(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    form_result.save()
  else:    
    password = form_result.cleaned_data.get("operatorPwd")
    permission = form_result.cleaned_data.get("operatorPerm")
    account = Account.objects.get(userID=username)
    account.rawPassword = password
    account.set_password(password)
    account.permission = permission
    account.isOpr = True
    account.save()
    POST_result[form_keyword] = OperatorForm()
  return POST_result
#=================================================================================#
def delete_operator(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    return POST_result
  
  account = Account.objects.get(userID=username)
  if account.isCpn or account.isSpl:
    account.permission = PERMISSION_LIST[0]
    account.isOpr = False
    account.save()
  else:
    account.delete()
    POST_result[form_keyword] = OperatorForm()
  return POST_result
#=================================================================================#

#=================================================================================#
#========== Specific actions for Suppliers: register/update/delete ===============#
def update_supplier(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    form_result.save()
  else:    
    password = form_result.cleaned_data.get("supplierPwd")
    supplier = form_result.cleaned_data.get("supplierName")
    account = Account.objects.get(userID=username)
    account.rawPassword = password
    account.set_password(password)
    account.supplierName = supplier
    account.isSpl = True
    account.save()
    POST_result[form_keyword] = SupplierForm()
  return POST_result
#=================================================================================#
def delete_supplier(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    return POST_result
  
  account = Account.objects.get(userID=username)
  if account.isOpr or account.isCpn:
    account.isSpl = False
    account.save()
  else:
    account.delete()
    POST_result[form_keyword] = SupplierForm()
  return POST_result
#=================================================================================#

#=================================================================================#
#========== Specific actions for Companies: register/update/delete ===============#
def update_company(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    form_result.save()
  else:    
    password = form_result.cleaned_data.get("companyPwd")
    email = form_result.cleaned_data.get("companyEmail")
    company = form_result.cleaned_data.get("companyName")
    vessels = form_result.cleaned_data.get("companyVessels")
    account = Account.objects.get(userID=username)
    account.rawPassword = password
    account.set_password(password)
    account.email = email
    account.companyName = company
    account.vesselList = vessels
    account.isCpn = True
    account.save()
    POST_result[form_keyword] = CompanyForm()
  return POST_result
#=================================================================================#
def delete_company(
    POST_result: dict, 
    form_keyword: str,
    username: str,
    n_targets: int=0,
) -> dict:
  form_result = POST_result[form_keyword]
  if n_targets<1:
    return POST_result
  
  account = Account.objects.get(userID=username)
  if account.isOpr or account.isSpl:
    account.isCpn = False
    account.save()
  else:
    account.delete()
    POST_result[form_keyword] = CompanyForm()
  return POST_result
#=================================================================================#