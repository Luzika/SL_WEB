from django import forms
from User.models import *
from User.forms import StaffLoginForm, CustomerLoginForm
from User.forms import OmegaRegistrationForm, OmegaModificationForm


LOGIN_PROCESS_DICT = {
  "staff": {
    "form": StaffLoginForm,
    "form_keyword": "staffLoginForm",
    "button_keywords": ["staffLogin"],
    "id_keyword": "staffID",
    "pwd_keyword": "staffPwd",
    "roleLogin": "staff",
  },
  "customer": {
    "form": CustomerLoginForm,
    "form_keyword": "customerLoginForm",
    "button_keywords": ["customerLogin"],
    "id_keyword": "customerID",
    "pwd_keyword": "customerPwd",
    "roleLogin": "customer",
  },
}
OMEGA_PROCESS_DICT = {
  "register": {
    "form": OmegaRegistrationForm,
    "form_keyword": "omegaRegistrationForm",
    "button_keywords": ["registerUser"],
    "id_keyword": "newID",  
  },
  "modify": {
    "form": OmegaModificationForm,
    "form_keyword": "omegaModificationForm",
    "button_keywords": ["modifyUser", "deleteUser"],
    "id_keyword": "MODuserID",  
  },
}


#=================================================================================#
#========== Specific format to handle the login request ==========================#
def setup_login_request(
    request,
    process_dict: dict,
) -> dict:
  form = process_dict["form"]
  form_keyword = process_dict["form_keyword"]
  button_keywords = process_dict["button_keywords"]
  id_keyword = process_dict["id_keyword"]
  pwd_keyword = process_dict["pwd_keyword"]

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
        result["_password"] = form_result.cleaned_data.get(pwd_keyword)
        result["_roleLogin"] = process_dict["roleLogin"]        
      else:
        form_result = form(request.POST)
      result[form_keyword] = form_result
  return result
#=================================================================================#

#=================================================================================#
#========== General format for Omega form (POST/GET) =============================#
def setup_omega_request(
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
#========== Specifics action by Omega User: modify/delete/register ===============#
def omega_modify(POST_result: dict, form_keyword: str, **kwargs) -> dict:
  field_keywords = kwargs["field_keywords"]
  fId, fPwd, fEmail, fCompany, fSupplier, fVessels, fPermission = field_keywords 
  fOpr = kwargs.get("fieldOpr", None)
  fSpl = kwargs.get("fieldSpl", None)
  fCpn = kwargs.get("fieldCpn", None)
  form_result = POST_result[form_keyword]

  # Collect core data
  username = form_result.cleaned_data.get(fId)
  password = form_result.cleaned_data.get(fPwd)
  email = form_result.cleaned_data.get(fEmail)
  company = form_result.cleaned_data.get(fCompany)
  supplier = form_result.cleaned_data.get(fSupplier)
  vessels = form_result.cleaned_data.get(fVessels)
  permission = form_result.cleaned_data.get(fPermission)
  # Check the role flags (Default=False if not specified)
  isOpr = False if not fOpr else form_result.cleaned_data.get(fOpr)
  isSpl = False if not fSpl else form_result.cleaned_data.get(fSpl)
  isCpn = False if not fCpn else form_result.cleaned_data.get(fCpn)
  
  account = Account.objects.get(userID=username)
  if password:
    account.set_password(password)
    account.rawPassword = password
  account.email = email
  account.companyName = company
  account.supplierName = supplier
  account.vesselList = vessels
  account.permission = permission
  account.isOpr = isOpr
  account.isSpl = isSpl
  account.isCpn = isCpn
  account.save()
  return POST_result
#=================================================================================#
def omega_delete(POST_result: dict, form_keyword: str) -> dict:
  username = POST_result["_username"]
  account = Account.objects.get(userID=username)
  account.delete()
  return POST_result
#=================================================================================#
def omega_register(POST_result: dict, form_keyword: str) -> dict:
  form_result = POST_result[form_keyword]
  # Note: FORM CAN ONLY BE SAVED AFTER CHECKING is_valid() EVEN IF ALREADY VALID
  if form_result.is_valid():
    form_result.save()
    POST_result[form_keyword] = OmegaRegistrationForm()
  return POST_result 
#=================================================================================#
