'''
- Validator functions check the input fields of the form 
- A validator will raise ValidationError if not satisfied
- Usually, the validator is applied in the clean_<field>() (<field>.errors)
- If clean() raises error, the errors will appear in the order of checking
'''

from django.forms import ValidationError as VE
from User.models import *
import re


#=================================================================================#
#========== General format of validators =========================================#
def digits_check_any(input_str: str, field_name: str="") -> None:
  field = "This input" if not field_name else field_name
  if not any(c.isdigit() for c in input_str):
    raise VE(field+" requires at least 1 number!")

def letters_check_any(input_str: str, field_name: str="") -> None:
  field = "This input" if not field_name else field_name
  if not any(c.isalpha() for c in input_str):
    raise VE(field+" requires at least 1 alphabet letter!")

def blank_check_all(input_str: str, field_name: str="") -> None:
  field = "This input" if not field_name else field_name
  if not input_str or all(c==" " for c in input_str):
    raise VE(field+" cannot be empty!")

def minimum_check(input_str: str, field_name: str="", min_length: int=4) -> None:
  field = "This input" if not field_name else field_name
  if len(input_str)<min_length:
    raise VE(field + f" must be at least {min_length} characters!")
  
def maximum_check(input_str: str, field_name: str="", max_length: int=LG) -> None:
  field = "This input" if not field_name else field_name
  if len(input_str)>max_length:
    raise VE(field + f" cannot exceed {max_length} characters!")
#=================================================================================#

#=================================================================================#
#========== Specific validators for user form ====================================#
def newID_validator(
    newID: str,
    min_length: int=4,
    max_length: int=MD,
) -> str:
  label = "Username"
  letters_check_any(newID, label)
  minimum_check(newID, label, min_length=min_length)
  maximum_check(newID, label, max_length=max_length)
  return newID

def newPwd_validator(
    newPwd: str,
    min_length: int=4,
    max_length: int=MD,
) -> str:
  label = "Password"
  digits_check_any(newPwd, label)
  minimum_check(newPwd, label, min_length=min_length)
  maximum_check(newPwd, label, max_length=max_length)
  return newPwd

def email_validator(
    email: str,
    max_length: int=MD,
) -> str:
  label = "Email"
  maximum_check(email, label, max_length=max_length)
  if email and "@" not in email:
    raise VE("Invalid format of email! No '@' sign?")
  return email

def company_validator(
    company: str,
    max_length: int=MD,
) -> str:
  label = "Company name"
  maximum_check(company, max_length=max_length)
  if company:
    letters_check_any(company, label)
  return company

def supplier_validator(
    supplier: str,
    max_length: int=MD,
) -> str:
  label = "Supplier name"
  maximum_check(supplier, max_length=max_length)
  if supplier:
    letters_check_any(supplier, label)
  return supplier

def vessels_validator(
    vessels: str,
    max_length: int=UL,
) -> str:
  label = "Vessel List"
  maximum_check(vessels, label, max_length=max_length)
  # if vessels and "," not in vessels:
  #   raise VE("There must be ',' among the vessels!")
  return vessels
#=================================================================================#
