from django import forms
from django.contrib.auth import authenticate
from User.models import *
from User.forms import StaffLoginForm, CustomerLoginForm


#=================================================================================#
#========== Split the views in the loginPage =====================================#
def user_login_view(
    request,
    form: forms.ModelForm, 
    id_field: str, 
    password_field: str,
    form_keyword: str, 
) -> dict:
  result: dict = {'userLogin': None, 'errorLogin': ""}

  if request.method=="POST":
    form_result = form(request.POST)
    if form_result.is_valid():
      username = form_result.cleaned_data.get(id_field)
      password = form_result.cleaned_data.get(password_field)
      account = authenticate(request, userID=username, password=password)
      if account is not None:
        result['userLogin'] = account
      else:
        result['errorLogin'] = "Wrong ID or password!"
    else:
      result['errorLogin'] = "Wrong ID or password!"
      form_result = form()
  
  else:
    form_result = form()
  
  result[form_keyword] = form_result
  return result


#=================================================================================#
#========== Assume that a staff is logging in ====================================#
def staff_login_request(
    request, 
    current_context: dict,
    form_reload: forms.ModelForm=StaffLoginForm,
    form_keyword: str="staffLoginForm",
) -> dict:
  result = dict(current_context)
  account = current_context.get('userLogin', None)

  if account:
    if not account.has_perm('User.can_modify'):
      result['errorLogin'] = "This account is not authorized here!"
      result[form_keyword] = form_reload()
  result['roleLogin'] = 1
  return result


#=================================================================================#
#========== Assume that a customer is logging in =================================#
def customer_login_request(
    request,
    current_context: dict,
    form_reload: forms.ModelForm=CustomerLoginForm,
    form_keyword: str="customerLoginForm",
) -> dict:
  result = dict(current_context)
  account = current_context.get('userLogin', None)

  if not account:
    result['errorLogin'] = "Wrong ID or password!"
    result[form_keyword] = form_reload()
  result['roleLogin'] = 2
  return result
