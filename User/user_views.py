from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from User.models import *
from User.models import get_dynamic_company_list
from User.form_views import *
from User.admin_views import *
from User.paginated_views import *
from Shipment.paginated_views import *
from django.contrib import messages
import os
import pickle
import pickle as pk
import json

# Configure logging
logger = logging.getLogger(__name__)

# Global context
CONTEXT = {'User': None, 'roleLogin': None}
CONTEXT["omegaUticked"] = {}
CONTEXT["omega0Uticked"] = {}
CONTEXT["shipmentTicked"] = {}
CONTEXT["shipment0Ticked"] = {}
CONTEXT["shipmentTickedNos"] = []
for i in range(1, 50):
    CONTEXT["omegaUticked"][i] = []
    CONTEXT["omega0Uticked"][i] = []
for i in range(1, 800):
    CONTEXT["shipmentTicked"][i] = []
    CONTEXT["shipment0Ticked"][i] = []
setup_permission(CONTEXT)
update_all_vessels(CONTEXT)

def defaultView(request):
    return redirect('loginPage')

@never_cache
def loginView(request):
    context = {}
    request.user = None
    CONTEXT['User'] = None
    CONTEXT['roleLogin'] = None
    reset_paginated_Sticks(CONTEXT, max_page_range=800)

    GET_results = [setup_login_request(request, request_case)
                   for request_case in LOGIN_PROCESS_DICT.values()]
    [context.update(GET_result) for GET_result in GET_results]

    if request.method == "POST":
        POST_results = [setup_login_request(request, request_case)
                        for request_case in LOGIN_PROCESS_DICT.values()]
        for POST_result in POST_results:
            if "_username" not in POST_result or not POST_result["_post"]:
                continue

            username = POST_result["_username"]
            password = POST_result["_password"]
            roleLogin = POST_result["_roleLogin"]
            account = authenticate(request, userID=username, password=password)
            if account is not None:
                if account.is_superuser:
                    CONTEXT["roleLogin"] = "staff"
                elif account.isOpr:
                    CONTEXT["roleLogin"] = "operator"
                elif account.isSpl:
                    CONTEXT["roleLogin"] = "supplier"
                elif account.isCpn:
                    CONTEXT["roleLogin"] = "company"
                else:
                    CONTEXT["roleLogin"] = roleLogin  # Fallback to form's role
                print(f"Login successful for user: {username} with role: {CONTEXT['roleLogin']}")
                login(request, account)
                return redirect("loginConfirmed", loggedID=account.userID, roleLogin=CONTEXT["roleLogin"])
    return render(request, "login.html", context)

def loggedIn(request, loggedID="0", roleLogin="staff"):
    return render(request, "loginConfirmed.html", {"loggedID": loggedID,
                                                  "roleLogin": roleLogin})

def loggedOut(request):
    logout(request)
    CONTEXT['User'] = None
    CONTEXT['roleLogin'] = None
    return redirect('default')

@never_cache
def adminView(request):
    context = {"roleLogin": CONTEXT["roleLogin"]}
    update_accounts(context)
    update_accounts_by_roles(context)
    context[PERMISSION_KW_JSON] = CONTEXT[PERMISSION_KW_JSON]

    # Load suppliers from database
    suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
    context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)  # JSON string for data-json
    context["suppliers_list"] = suppliers  # Python list for iteration
    context["supplierForm"] = SupplierForm()

    roles = ["operator", "supplier", "company"]

    for role in roles:
        request_case = ADMIN_PROCESS_DICT[role]
        GET_result = setup_admin_request(request, request_case)
        context.update(GET_result)

    if request.method == "POST":
        if "addSupplierMod" in request.POST:
            supplier_name = request.POST.get("supplierName", "").strip()
            if not supplier_name:
                messages.error(request, "Supplier name cannot be empty.")
            elif Supplier.objects.filter(name=supplier_name).exists():
                messages.error(request, f"Supplier '{supplier_name}' already exists.")
            else:
                Supplier.objects.create(name=supplier_name)
                suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
                context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)
                context["suppliers_list"] = suppliers
                messages.success(request, f"Supplier '{supplier_name}' added successfully.")
            return render(request, "admin.html", context)

        elif "modifySupplierMod" in request.POST:
            old_name = request.POST.get("old_supplierName", "").strip()
            new_name = request.POST.get("supplierName", "").strip()
            if not new_name:
                messages.error(request, "New supplier name cannot be empty.")
            elif not old_name:
                messages.error(request, "Please select a supplier to modify.")
            elif Supplier.objects.filter(name=new_name).exists() and new_name != old_name:
                messages.error(request, f"Supplier '{new_name}' already exists.")
            else:
                supplier = Supplier.objects.filter(name=old_name).first()
                if supplier:
                    supplier.name = new_name
                    supplier.save()
                    # Update related Shipment records
                    Shipment.objects.filter(supplier=old_name).update(supplier=new_name)
                    suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
                    context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)
                    context["suppliers_list"] = suppliers
                    messages.success(request, f"Supplier '{old_name}' modified to '{new_name}'.")
                else:
                    messages.error(request, f"Supplier '{old_name}' not found.")
            return render(request, "admin.html", context)

        elif "deleteSupplierMod" in request.POST:
            supplier_name = request.POST.get("old_supplierName", "").strip()
            if not supplier_name:
                messages.error(request, "Please select a supplier to delete.")
            else:
                supplier = Supplier.objects.filter(name=supplier_name).first()
                if supplier:
                    supplier.delete()
                    suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
                    context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)
                    context["suppliers_list"] = suppliers
                    messages.success(request, f"Supplier '{supplier_name}' deleted successfully.")
                else:
                    messages.error(request, f"Supplier '{supplier_name}' not found.")
            return render(request, "admin.html", context)

        for role in roles:
            request_case = ADMIN_PROCESS_DICT[role]
            POST_result = setup_admin_request(request, request_case)
            if "_username" not in POST_result or not POST_result["_post"]:
                continue

            username = POST_result["_username"]
            form_keyword = request_case["form_keyword"]
            n_targets = len(Account.objects.filter(userID=username))
            if POST_result["_clicked"] == "saveOperator":
                update_operator(POST_result, form_keyword, username, n_targets)
            if POST_result["_clicked"] == "deleteOperator":
                delete_operator(POST_result, form_keyword, username, n_targets)
            if POST_result["_clicked"] == "saveSupplier":
                update_supplier(POST_result, form_keyword, username, n_targets)
            if POST_result["_clicked"] == "deleteSupplier":
                delete_supplier(POST_result, form_keyword, username, n_targets)
            if POST_result["_clicked"] == "saveCompany":
                update_company(POST_result, form_keyword, username, n_targets)
                update_all_vessels(CONTEXT)  # Refresh vessel list after company update
                refresh_dynamic_lists(CONTEXT) # <--- ADD THIS CALL
            if POST_result["_clicked"] == "deleteCompany":
                delete_company(POST_result, form_keyword, username, n_targets)
                update_all_vessels(CONTEXT)  # Refresh vessel list after company deletion
                refresh_dynamic_lists(CONTEXT) # <--- ADD THIS CALL

            context.update(POST_result)
            update_accounts(context)
            update_accounts_by_roles(context)
            return render(request, "admin.html", context)
        
        # Refresh dynamic lists for suppliers and vessels
        refresh_dynamic_lists(context)

    response = render(request, "admin.html", context)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

def refresh_dynamic_lists(context):
    """
    Refreshes the global CONTEXT with the latest company and vessel data from the database.
    """
    # 1. Update company list
    dynamic_companies = get_dynamic_company_list()
    context['prelistCompanies'] = json.dumps(dynamic_companies)
    
    # 2. Update vessel list (since company list changed, vessel list also needs update)
    update_all_vessels(context) 

@never_cache
def omegaManageView(request):
  context = {"roleLogin": CONTEXT["roleLogin"]}
  update_accounts(context)
  context[PERMISSION_KW_JSON] = CONTEXT[PERMISSION_KW_JSON]

  GET_results = [setup_omega_request(request, request_case)
                 for request_case in OMEGA_PROCESS_DICT.values()]
  [context.update(GET_result) for GET_result in GET_results]

  if request.method=="POST":
    MOD_field_keywords = [
      "MODuserID", "MODnewPwd", "MODemail",
      "MODcompany", "MODsupplier","MODvesselList", "MODpermission"]
    fieldOpr, fieldSpl, fieldCpn = "MODisOpr", "MODisSpl", "MODisCpn"
    POST_results = [setup_omega_request(request, request_case)
                    for request_case in OMEGA_PROCESS_DICT.values()]
    for POST_results in POST_results:
      if "_username" not in POST_result or not POST_result["_post"]:
        continue

      if POST_result["_clicked"] == "deleteUser":
        omega_delete(POST_result, "omegaModificationForm")
      if POST_result["_clicked"] == "registerUser":
        omega_register(POST_result, "omegaRegistrationForm")
      if POST_result["_clicked"] == "modifyUser":
        omega_modify(POST_result, "omegaModificationForm",
                     field_keywords=MOD_field_keywords,
                     fieldOpr=fieldOpr, fieldSpl=fieldSpl, fieldCpn=fieldCpn)

      context.update(POST_result)
      update_accounts(context)
      return render(request, "omega.html", context)
  return render(request, "omega.html", context)

def omegaMonitorView(request):
  context = {"roleLogin": CONTEXT["roleLogin"]}
  if "page" not in request.GET:
    reset_paginated_Uticks(CONTEXT, max_page_range=50)

  PAG_account_result = paginate_account(
    request, CONTEXT, "pageUticked", "page0Uticked",
    "accountsPage", "allTickedIDs")
  context.update(PAG_account_result)
  context["allTickedAccounts"] = [
    Account.objects.get(userID=userID) for userID in context["allTickedIDs"]
  ]

  if request.POST:
    if "exportExcelUser" in request.POST:
      return paginate_account_Excel(request, context, "allTickedAccounts")
    if "multiDeleteUser" in request.POST:
      paginate_account_delete(request, context, "allTickedAccounts")

    reset_paginated_Uticks(CONTEXT, max_page_range=50)
    PAG_account_result = paginate_account(
      request, CONTEXT, "pageUticked", "page0Uticked",
      "accountsPage", "allTickedIDs")
    context.update(PAG_account_result)
    return render(request, "omegaMonitor.html", context)

  return render(request, "omegaMonitor.html", context)

def omegaDownloaded(request):
  return render(request, "omegaDownloaded.html", {})