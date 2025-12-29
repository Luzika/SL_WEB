from django import forms
from django.forms import TextInput, PasswordInput, Textarea
from django.forms import CharField, BooleanField
from django.forms import ValidationError
from django.contrib.auth import authenticate

from User.models import *
from User.form_validators import *


def set_form_CSS(
    form: forms.ModelForm, 
    field_name: str,
    class_css: str="", 
    style_css: str="",
) -> None:
  if class_css:
    form.fields[field_name].widget.attrs['class'] = class_css
  if style_css:
    form.fields[field_name].widget.attrs['style'] = style_css


#=================================================================================#
#========== Login Forms (frontPage) ==============================================#
class StaffLoginForm(forms.ModelForm):
  staffID = CharField(label="Staff ID", widget=TextInput)
  staffPwd = CharField(label="Password", widget=PasswordInput)

  class Meta:
    model = Account
    fields = ('staffID', 'staffPwd')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields:
      set_form_CSS(self, field,
                   class_css="loginField",
                   style_css="width: 100%;")

  def clean(self):
    if self.is_valid():
      username = self.cleaned_data.get('staffID')
      password = self.cleaned_data.get('staffPwd')
      account = authenticate(userID=username, password=password)
      if not account:
        raise ValidationError(f"Invalid staff account. \nPlease try again!")
      if not account.isOpr: #or not account.is_superuser:
        raise ValidationError("Sorry, this account is not authorized here!")
#=================================================================================#

#=================================================================================#
class CustomerLoginForm(forms.ModelForm):
  customerID = CharField(label="Customer ID", widget=forms.TextInput)
  customerPwd = CharField(label="Password", widget=forms.PasswordInput)

  class Meta:
    model = Account
    fields = ('customerID', 'customerPwd')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields:
      set_form_CSS(self, field,
                   class_css="loginField",
                   style_css="width: 100%;")
      
  def clean(self):
    if self.is_valid():
      username = self.cleaned_data.get('customerID')
      password = self.cleaned_data.get('customerPwd')
      if not authenticate(userID=username, password=password):
        raise ValidationError(f"Invalid customer account. \nPlease try again!")
#=================================================================================#


#========== Update Forms (adminPage) =============================================#
#=================================================================================#
class OperatorForm(forms.ModelForm):
  operatorID = forms.CharField(widget=TextInput, max_length=SM)
  operatorPwd = forms.CharField(widget=TextInput, max_length=MD)
  operatorPerm = forms.CharField(widget=TextInput, max_length=MD)

  class Meta:
    model = Account
    fields = ('operatorID', 'operatorPwd', 'operatorPerm')

  def clean_operatorPwd(self):
    return newPwd_validator(self.cleaned_data.get('operatorPwd'), min_length=3)

  def save(self, commit=True):
    super().save(commit=False)
    username = self.cleaned_data.get('operatorID')
    password = self.cleaned_data.get('operatorPwd')
    permission = self.cleaned_data.get('operatorPerm')
    
    account = Account.objects.create(
      userID=username, 
      rawPassword=password,
      permission=permission, 
      isOpr=True,
    )

    if commit:
      account.set_password(password)
      account.save()
    return account
#=================================================================================#
  
#=================================================================================#
class SupplierForm(forms.ModelForm):
  supplierID = forms.CharField(widget=TextInput, max_length=SM)
  supplierPwd = forms.CharField(widget=TextInput, max_length=MD)
  supplierName = forms.CharField(widget=TextInput, max_length=MD)

  class Meta:
    model = Account
    fields = ('supplierID', 'supplierPwd', 'supplierName')
    
  def clean_supplierPwd(self):
    return newPwd_validator(self.cleaned_data.get('supplierPwd'), min_length=3)
  def clean_supplierName(self):
    return supplier_validator(self.cleaned_data.get('supplierName'))
  
  def save(self, commit=True):
    super().save(commit=False)
    username = self.cleaned_data.get('supplierID')
    password = self.cleaned_data.get('supplierPwd')
    supplier = self.cleaned_data.get('supplierName')
    permission = PERMISSION_LIST[0]

    account = Account.objects.create(
      userID=username, 
      rawPassword=password,
      supplierName=supplier,
      permission=permission,
      isSpl=True,
    )

    if commit:
      account.set_password(password)
      account.save()
    return account
#=================================================================================#

#=================================================================================#
class CompanyForm(forms.ModelForm):
  companyID = forms.CharField(widget=TextInput, max_length=SM)
  companyPwd = forms.CharField(widget=TextInput, max_length=MD)
  companyName = forms.CharField(widget=TextInput, max_length=MD)
  companyEmail = forms.CharField(widget=TextInput, max_length=MD)
  companyVessels = forms.CharField(widget=Textarea, max_length=UL)

  class Meta:
    model = Account
    fields = ('companyID', 'companyPwd', 'companyName', 
              'companyEmail', 'companyVessels')
    
  def clean_companyPwd(self):
    return newPwd_validator(self.cleaned_data.get('companyPwd'), min_length=3)
  def clean_companyName(self):
    return company_validator(self.cleaned_data.get('companyName'))
  def clean_companyEmail(self):
    return email_validator(self.cleaned_data.get('companyEmail'))
  def clean_companyVessels(self):
    return vessels_validator(self.cleaned_data.get('companyVessels'))
    
  def save(self, commit=True):
    super().save(commit=False)
    username = self.cleaned_data.get('companyID')
    password = self.cleaned_data.get('companyPwd')
    company = self.cleaned_data.get('companyName')
    email = self.cleaned_data.get('companyEmail')
    vessels = self.cleaned_data.get('companyVessels')
    permission = PERMISSION_LIST[0]

    account = Account.objects.create(
      userID=username, 
      rawPassword=password,
      permission=permission,
      email=email,
      isCpn=True,
      companyName=company,
      vesselList=vessels,
    )

    if commit:
      account.set_password(password)
      account.save()
    return account
#=================================================================================#


#=================================================================================#
# Note: this registration form is only for Omega account 
class OmegaRegistrationForm(forms.ModelForm):
  newID = CharField(widget=TextInput, max_length=SM)
  newPwd = CharField(widget=PasswordInput, max_length=MD)
  newPwd2 = CharField(widget=PasswordInput, max_length=MD)
  # Note: if required=True, Boolean Fields MUST BE CLICKED ON!
  isOpr = BooleanField(initial=False, required=False)
  isSpl = BooleanField(initial=False, required=False)
  isCpn = BooleanField(initial=False, required=False)

  class Meta:
    model = Account
    fields = ('newID', 'newPwd', 'newPwd2', 'email', 'isOpr', 'isSpl', 'isCpn',
              'companyName', 'supplierName', 'vesselList', 'permission')

  # Note: using field validators must explicitly define clean_<field>() to apply
  def clean_newID(self):
    return newID_validator(self.cleaned_data.get('newID'))
  def clean_newPwd(self):
    return newPwd_validator(self.cleaned_data.get('newPwd'))
  def clean_email(self):
    return email_validator(self.cleaned_data.get('email'))
  def clean_companyName(self):
    return company_validator(self.cleaned_data.get('companyName'))
  def clean_supplierName(self):
    return supplier_validator(self.cleaned_data.get('supplierName'))
  def clean_vesselList(self):
    return vessels_validator(self.cleaned_data.get('vesselList'))

  def clean(self):
    if self.is_valid():
      password = self.cleaned_data.get('newPwd')
      password2 = self.cleaned_data.get('newPwd2')
      if password2 != password:
        raise ValidationError("Please confirm the password twice correctly!")
      
  def save(self, commit=True):
    super().save(commit=False)
    username = self.cleaned_data.get('newID')
    password = self.cleaned_data.get('newPwd')
    permission = list(PERMISSION_DICT.keys())[0]
    email = self.cleaned_data.get('email')
    company = self.cleaned_data.get('companyName')
    supplier = self.cleaned_data.get('supplierName')
    vesselList = self.cleaned_data.get('vesselList')
    isOpr = self.cleaned_data.get('isOpr')
    isSpl = self.cleaned_data.get('isSpl')
    isCpn = self.cleaned_data.get('isCpn')

    account = Account.objects.create(
      userID=username,
      rawPassword=password,
      email=email,
      companyName=company,
      supplierName=supplier,
      vesselList=vesselList,
      permission=permission,
      isOpr=isOpr, isSpl=isSpl, isCpn=isCpn,
    )

    if commit:
      account.set_password(password)
      account.save()
    return account    
#=================================================================================#

#=================================================================================#
# Note: this modification form is only for Omega account 
class OmegaModificationForm(forms.ModelForm):
  MODuserID = CharField(widget=TextInput, max_length=SM)
  MODnewPwd = CharField(widget=TextInput, max_length=MD, required=False)
  MODemail = CharField(widget=TextInput, max_length=MD, required=False)
  MODcompany = CharField(widget=TextInput, max_length=MD, required=False)
  MODsupplier = CharField(widget=TextInput, max_length=MD, required=False)
  MODpermission = CharField(widget=TextInput, max_length=MD, required=True)
  MODvesselList = CharField(widget=Textarea, max_length=UL, required=False)
  # Note: if required=True, Boolean Fields MUST BE CLICKED ON!
  MODisOpr = BooleanField(initial=False, required=False)
  MODisSpl = BooleanField(initial=False, required=False)
  MODisCpn = BooleanField(initial=False, required=False)
  
  class Meta:
    model = Account
    fields = ('MODuserID', 'MODnewPwd', 'MODemail', 'MODvesselList', 
              'MODpermission', 'MODcompany', 'MODsupplier', 
              'MODisOpr', 'MODisSpl', 'MODisCpn')
#=================================================================================#