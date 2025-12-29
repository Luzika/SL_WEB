'''
- Model is used to save data into database
- In Django, there must be an app used for authentication (main app)
- Main app can be named as desired, but usually "User"
- The model for User can be named as desired. In this case: "Account"
- User model is important as it is used to authenticate for login/logout
- User model must be registered in the settings.py: AUTH_USER_MODEL='User.Account'
- Every User model needs a manager class to handle save/delete/get/sort/filter/...
- User model usually subclass AbstractBaseUser and BaseUserManager for full control
- blank=True means that the field can be left empty in the database
- null=True means that the empty field will be stored as NULL in the database
'''
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Permission, PermissionsMixin
from django.contrib.auth.models import AbstractUser

import json, re


MAX_LENGTH_FIELDS = {
  "SM": 12,
  "MD": 30,
  "LG": 100,
  "XL": 1000,
  "UL": 2000,
}
PERMISSION_DICT = {
  "Read Only": {
    "code": "read_only",
    "desc": "Can only read orders",
  },
  "Read + Modify": {
    "code": "can_modify",
    "desc": "Can create & modify the orders",
  },
}
PERMISSION_CHOICES = {pm:pm for pm in PERMISSION_DICT}
PERMISSION_CHOICES0 = [(pm,pm) for pm in PERMISSION_DICT]
PERMISSION_LIST = list(PERMISSION_DICT.keys())


# Create your models here.
SM = MAX_LENGTH_FIELDS["SM"]
MD = MAX_LENGTH_FIELDS["MD"]
LG = MAX_LENGTH_FIELDS["LG"]
XL = MAX_LENGTH_FIELDS["XL"]
UL = MAX_LENGTH_FIELDS["UL"]
ACCOUNT_KW_JSON = "Accounts"
ACCOUNT_KW_DATA = "allAccounts"
PERMISSION_KW_JSON = "Permissions"
PERMISSION_KW_DATA = "allPermissions"


#=================================================================================#
#========== This class manages the User model (get, save, filter, ...) ===========#
### Subclassing BaseUserManager must include create_user() and create_superuser()
class AccountManager(BaseUserManager):
  def create_user(self, userID, password, **extra_fields):
    if not userID:
      raise ValueError("Account ID must be set!")
    account = self.model(userID=userID, **extra_fields)
    account.rawPassword = password
    account.set_password(password)
    permission =  extra_fields.get('permission', list(PERMISSION_DICT.keys())[0])
    account.permission = permission

    account.save(using=self.db)
    return account

  # Create a superuser from the console (allow to skip the validators)
  def create_superuser(self, userID, password, **extra_fields):
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('isOpr', True)
    extra_fields.setdefault('permission', list(PERMISSION_DICT.keys())[1])
    superAccount = self.create_user(userID, password, **extra_fields)
    superAccount.save(using=self.db)
    return superAccount


#=================================================================================#
#========== Main model for User with Permission class ============================#
### Subclassing AbstractBaseUser automatically include last_login and is_superuser
class Account(AbstractBaseUser, PermissionsMixin):
  # Note: primary_key=True <=> null=False, unique=True
  # Every model must have a primary field.
  # If not specified, one extra column for indexing will be added as primary field
  userID = models.CharField(verbose_name="AccountID", primary_key=True,
                            max_length=SM)
  rawPassword = models.CharField(verbose_name="Password",
                                 max_length=MD)
  # email = models.EmailField(verbose_name="Email", blank=True,
  #                           max_length=MD)
  email = models.CharField(verbose_name="Email", blank=True,
                           max_length=MD)
  companyName = models.CharField(verbose_name="Company", blank=True,
                                 max_length=MD)
  supplierName = models.CharField(verbose_name="Supplier", blank=True,
                                 max_length=MD)
  vesselList = models.TextField(verbose_name="Vessel List", blank=True,
                                max_length=UL)

  permission = models.CharField(verbose_name="Permission",
                                max_length=MD,
                                choices=PERMISSION_CHOICES0,
                                default=list(PERMISSION_DICT.keys())[0])
  isOpr = models.BooleanField(verbose_name="Is Operator", default=False)
  isSpl = models.BooleanField(verbose_name="Is Supplier", default=False)
  isCpn = models.BooleanField(verbose_name="Is Company", default=False)
  dateSignUp = models.DateField(verbose_name="Date Signed Up", auto_now=True)

  # Must have this manager class in the model definition
  objects = AccountManager()

  # The identifier field for User (must be unique -> userID)
  USERNAME_FIELD = "userID"
  # Add aditional required fields for User (not including userID)
  REQUIRED_FIELDS = []

  # Define metadata for the model
  class Meta:
    # Database name for the model
    db_table = "sl_users"
    # Permissions set for the model
    default_permissions = []
    permissions = [(pm["code"],pm["desc"]) for pm in PERMISSION_DICT.values()]

  # Define an interpretation when printing
  def __str__(self):
    omega_role = "Omega" if self.is_superuser else ""
    opr_role = ", Operator" if self.isOpr else ""
    spl_role = ", Supplier" if self.isSpl else ""
    cpn_role = ", Company" if self.isCpn else ""
    return f"User {self.userID}: " + omega_role + opr_role + spl_role + cpn_role
#=================================================================================#


#=================================================================================#
#========== Update database into context =========================================#
def update_accounts(
    context: dict,
    data_keyword: str=ACCOUNT_KW_DATA,
    json_keyword: str=ACCOUNT_KW_JSON,
) -> None:
  all_accounts = Account.objects.all().order_by("dateSignUp")

  # Note: this is the general format to transfer backend data into HTML for frontend
  context[data_keyword] = all_accounts
  # Note: this is the general format to transfer backend data into JSON for frontend
  context[json_keyword] = json.dumps(
    [
      {
        "userID": account.userID,
        "password": account.rawPassword,
        "permission": account.permission,
        "email": account.email,
        "company": account.companyName,
        "supplier": account.supplierName,
        "vessels": account.vesselList,
        "isOpr": account.isOpr,
        "isSpl": account.isSpl,
        "isCpn": account.isCpn,
      }
      for account in all_accounts
    ]
  )
#=================================================================================#
def update_accounts_by_roles(context: dict) -> None:
  all_accounts = Account.objects.all().order_by("dateSignUp")
  all_operators = all_accounts.filter(isOpr=True).filter(is_superuser=False)
  all_suppliers = all_accounts.filter(isSpl=True).filter(is_superuser=False)
  all_companies = all_accounts.filter(isCpn=True).filter(is_superuser=False)

  context["Operators"] = json.dumps(
    [
      {
        "userID": account.userID,
        "password": account.rawPassword,
        "permission": account.permission,
      }
      for account in all_operators
    ]
  )
  context["Suppliers"] = json.dumps(
    [
      {
        "userID": account.userID,
        "password": account.rawPassword,
        "supplier": account.supplierName,
      }
      for account in all_suppliers
    ]
  )

  delimiters = r',\s*'
  context["Companies"] = json.dumps(
    [
      {
        'userID': account.userID,
        'password': account.rawPassword,
        'email': account.email,
        'company': account.companyName,
        'vesselList': account.vesselList,
      }
      for account in all_companies
    ]
  )
#=================================================================================#
def update_all_vessels(context: dict):
  delimiters = r',\s*'
  context['vesselsDB'] = []

  all_accounts = Account.objects.all()
  for account in all_accounts:
    if account.vesselList:
      company = account.companyName
      split_vessels = re.split(delimiters, account.vesselList)
      vessels = [ves for ves in split_vessels if ves]
      context['vesselsDB'].extend(vessels)
      for vessel in vessels:
        context[vessel] = company

  context['VesselMap'] = json.dumps(
    [
      {
        "vessel": ves,
        "vesselOwner": context[ves],
      }
      for ves in context["vesselsDB"]
    ]
  )
  context['vesselsDB'] = list(dict.fromkeys(context['vesselsDB']))
  context['VesselsDB'] = json.dumps(context['vesselsDB'])
#=================================================================================#
def setup_permission(
    context: dict,
    data_keyword: str=PERMISSION_KW_DATA,
    json_keyword: str=PERMISSION_KW_JSON,
) -> None:
  # Note: this is the general format to transfer backend data into HTML for frontend
  context[data_keyword] = PERMISSION_LIST
  # Note: this is the general format to transfer backend data into JSON for frontend
  context[json_keyword] = json.dumps(
    [
      {
        "level": permission_level,
      }
      for permission_level in PERMISSION_LIST
    ]
  )
#=================================================================================#
#========== Model for Supplier Names =============================================#
class Supplier(models.Model):
    name = models.CharField(max_length=LG, unique=True, verbose_name="Supplier Name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="suppliers", verbose_name="Associated Account")

    class Meta:
        db_table = "sl_suppliers"
        ordering = ["name"]

    def __str__(self):
        return self.name

#=================================================================================#
#========== Function to update all company names from Accounts ===================#
def get_dynamic_company_list():
  """
  Retrieves a list of all unique, non-empty company names from the Account model.
  """
  # Fetch all unique, non-empty company names where the account is marked as a Company (isCpn=True)
  # or where a company name is explicitly provided.
  # This uses .values_list('companyName', flat=True) to get a list of strings
  # and .distinct() to ensure no duplicates.
  companies = list(
    Account.objects.filter(
      Q(isCpn=True) | Q(companyName__isnull=False)
    )
    .exclude(companyName__exact='') # Exclude empty strings
    .values_list('companyName', flat=True)
    .order_by('companyName')
    .distinct()
  )
  
  # Optionally, you can include companies from the Supplier model if it has a company-like role
  # The snippet shows a Supplier model, but for now, we'll focus on companyName in Account
  
  return companies
#=================================================================================#