from urllib import request
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django_user_agents.utils import get_user_agent
from django.contrib import messages
from django.db import transaction, IntegrityError
from User.models import *
from User.views import CONTEXT
from Shipment.models import *
from Shipment.form_views import *
from Shipment.paginated_views import *
from Shipment.forms import ShipmentRegistrationForm, ShipmentModificationForm, PendingShipmentForm
import pandas as pd
import json
from pathlib import Path
import pickle as pk
from django.core import serializers
from dateutil.parser import parse as parse_date
from datetime import datetime
import logging
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Shipment, ShipmentMovement, ShipmentEvaluation
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
# Now, dynamically fetch the companies:
from User.models import get_dynamic_company_list
from Shipment.models import PendingShipment
from User.models import Account
from urllib.parse import parse_qs
from django.http import QueryDict
# Configure logging
logger = logging.getLogger(__name__)

# Extract prelist values into a global context for fast processing
dynamic_companies = get_dynamic_company_list()
CONTEXT['prelistCompanies'] = json.dumps(dynamic_companies)
CONTEXT['prelistDivisions'] = json.dumps(DIVISION_LIST)
CONTEXT['prelistWarehouses'] = json.dumps(WAREHOUSE_LIST)
CONTEXT['prelistFlags'] = json.dumps(FLAG_LIST)
CONTEXT['prelistCPacking'] = json.dumps(CPACKING_LIST)
CONTEXT["prelistBys"] = json.dumps(BY_LIST)
CONTEXT["prelistUnits"] = json.dumps(UNIT_LIST)
update_all_vessels(CONTEXT)

def generate_shipment_id(company, vessel, in_date):
    # Use current time as HHMMSS (6 digits)
    current_time = datetime.datetime.now().strftime('%H%M%S')
    sequence = current_time  # e.g., '143022' for 14:30:22

    # Company code: first 2 letters, pad with X if too short
    company_code = (company[:2] if len(company) >= 2 else company + 'XX')[:2].upper()

    # Vessel code
    vessel_words = vessel.strip().split() if vessel else []
    if len(vessel_words) == 2:
        vessel_code = (vessel_words[0][:1] or 'X')[:1].upper() + (vessel_words[1][:1] or 'X')[:1].upper()
    else:
        vessel_code = (vessel[:2] if vessel and len(vessel) >= 2 else (vessel + 'XX' if vessel else 'XX'))[:2].upper()

    # Date part: last 6 digits of YYYYMMDD → YYMMDD
    date_str = in_date.strftime('%Y%m%d')[2:] if in_date else '000000'

    # Final ID: HHMMSS + Company(2) + Vessel(2) + YYMMDD
    return f"{sequence}{company_code}{vessel_code}{date_str}"

def shipmentTrackingView(request, shipment_id):
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    shipment.refresh_from_db()
    movements = shipment.movements.all().order_by('timestamp')
    evaluation = None
    if shipment.flag_status == 'COMPLETED':
        evaluation = ShipmentEvaluation.objects.filter(shipment=shipment).first()
    logger.debug(f"Rendering shipment {shipment_id} with {movements.count()} movements and evaluation: {evaluation}")
    context = {
        'shipment': shipment,
        'movements': movements,
        'evaluation': evaluation,
    }
    return render(request, 'shipmentTracking.html', context)

def preprocess_yymmdd_to_yyyymmdd(date_str):
    """
    Convert a YYMMDD date string (e.g., '241126') to YYYYMMDD (e.g., '20241126').
    Returns the converted string if successful, otherwise returns the original string.
    """
    date_str = str(date_str).strip()
    if date_str.isdigit() and len(date_str) == 6:
        try:
            year_prefix = "20"
            return f"{year_prefix}{date_str}"
        except (ValueError, TypeError):
            return date_str
    return date_str


def mainView1(request):
    useragent = get_user_agent(request)

    if not (request.user.isOpr or request.user.is_superuser):  # Ensure staff access
        return redirect('mainPage2')
    
    context = {k: CONTEXT[k] for k in CONTEXT.keys()}
    context["roleLogin"] = "staff"
    context["shipmentRegForm"] = ShipmentRegistrationForm()
    context["shipmentRegFormM"] = ShipmentRegistrationForm()
    context["shipmentModForm"] = ShipmentModificationForm()
    context['pending_shipments'] = PendingShipment.objects.all()

    # Helper to redirect back to main page preserving current GET querystring when available
    def pr(name='mainPage1'):
        try:
            qs = request.GET.urlencode()
            if not qs:
                ref = request.META.get('HTTP_REFERER', '')
                if '?' in ref:
                    qs = ref.split('?', 1)[1]
            if qs:
                return redirect(f"{reverse(name)}?{qs}")
        except Exception:
            pass
        return redirect(name)

    # Load suppliers
    suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
    context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)
    context["suppliers_list"] = suppliers

    filter_show = filter_shipment(request, "shipmentFilterForm", "shipmentPage", "shipmentResults")
    context['totalResults'] = len(filter_show["shipmentResults"])
    context.update(filter_show)
    page_num = filter_show["page_num"]

    # Initialize session data
    if "shipmentTickedNos" not in request.session:
        request.session["shipmentTickedNos"] = []
        request.session.modified = True
    if "shipmentTicked" not in request.session:
        request.session["shipmentTicked"] = {}
        request.session.modified = True
    if "shipment0Ticked" not in request.session:
        request.session["shipment0Ticked"] = {}
        request.session.modified = True

    # Sync CONTEXT with session
    CONTEXT["shipmentTickedNos"] = request.session["shipmentTickedNos"]
    logger.info(f"mainView1: Session shipmentTickedNos: {request.session['shipmentTickedNos']}")

    # Log context and request data for GET requests
    if request.method == "GET":
        logger.debug(f"mainView1 GET: Context allTickedNos: {context.get('allTickedNos')}, Request GET: {request.GET}, Request POST: {request.POST}")

    # Set allTickedNos from session
    context["allTickedNos"] = request.session["shipmentTickedNos"]
    if not context["allTickedNos"]:
        context["allTickedShipments"] = []
    else:
        try:
            ticked_nos = [int(no) for no in context["allTickedNos"]]
            shipments = Shipment.objects.filter(number__in=ticked_nos)
            context["allTickedShipments"] = list(shipments)
            logger.info(f"mainView1: Retrieved {len(context['allTickedShipments'])} allTickedShipments for {len(ticked_nos)} allTickedNos")
        except Exception as e:
            logger.error(f"mainView1: Error fetching allTickedShipments: {e}")
            context["allTickedShipments"] = []

    if request.method == "POST":
        logger.info("mainView1: Received POST request")
        logger.debug(f"mainView1: POST data: {request.POST}")
        logger.info(f"mainView1: Session before POST: {request.session.get('shipmentTickedNos', [])}")

        # Handle AJAX checkbox updates
        if "update_selection" in request.POST:
            shipment_number = request.POST.get("shipment_number")
            is_checked = request.POST.get("is_checked") == "true"
            current_selections = request.session.get("shipmentTickedNos", [])

            try:
                shipment_number = int(shipment_number)
                if is_checked and shipment_number not in current_selections:
                    current_selections.append(shipment_number)
                elif not is_checked and shipment_number in current_selections:
                    current_selections.remove(shipment_number)
                request.session["shipmentTickedNos"] = list(set(current_selections))
                request.session.modified = True

                # Update page-specific selections
                page_num = request.POST.get("page", str(page_num))
                list_ticked = request.POST.get("pageSticked", "")
                list_unticked = request.POST.get("page0Sticked", "")
                ticked_ids = [int(id) for id in list_ticked.split(",") if id] if list_ticked else []
                unticked_ids = [int(id) for id in list_unticked.split(",") if id] if list_unticked else []
                request.session["shipmentTicked"][page_num] = ticked_ids
                request.session["shipment0Ticked"][page_num] = unticked_ids
                request.session.modified = True

                return JsonResponse({"status": "success"})
            except (ValueError, TypeError) as e:
                logger.error(f"mainView1: Error updating selection: {e}")
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
        # Handle Bulk Approve
        if "bulk_approve" in request.POST:
            selected_pks = request.POST.getlist('selected_pending')
            if not selected_pks:
                messages.warning(request, "No pending shipments selected for approval.")
                return pr()
            
            approved_count = 0
            with transaction.atomic():
                for pk in selected_pks:
                    try:
                        pending = get_object_or_404(PendingShipment, pk=pk)
                        shipment = Shipment(
                            company=pending.company,
                            vessel=pending.vessel,
                            supplier=pending.supplier,
                            quanty=pending.quanty,
                            weight=pending.weight,
                            size=pending.size,
                            flag_status='BLANK',  # Default status
                            c_packing='',  # Set empty string as default
                            insert_org=pending.submitted_by.userID,
                            correct_org=request.user.userID,
                            # Add other defaults as needed
                        )
                        shipment.save()
                        pending.delete()
                        approved_count += 1
                    except Exception as e:
                        logger.error(f"Error approving pending shipment {pk}: {e}")
                        messages.error(request, f"Failed to approve shipment {pk}: {str(e)}")
            
            if approved_count > 0:
                messages.success(request, f"{approved_count} pending shipments approved and added to database.")
            return pr()

        # Handle Bulk Reject
        if "bulk_reject" in request.POST:
            selected_pks = request.POST.getlist('selected_pending')
            if not selected_pks:
                messages.warning(request, "No pending shipments selected for rejection.")
                return pr()
            
            rejected_count = 0
            with transaction.atomic():
                for pk in selected_pks:
                    try:
                        pending = get_object_or_404(PendingShipment, pk=pk)
                        pending.delete()
                        rejected_count += 1
                    except Exception as e:
                        logger.error(f"Error rejecting pending shipment {pk}: {e}")
                        messages.error(request, f"Failed to reject shipment {pk}: {str(e)}")
            
            if rejected_count > 0:
                messages.success(request, f"{rejected_count} pending shipments rejected and deleted.")
            return pr()

        # Handle export first to avoid overwriting allTickedNos
        if "exportExcelShipment" in request.POST:
            logger.info("mainView1: ExportExcelShipment button clicked")

            all_ticked_nos = request.POST.get("allTickedNos", "")
            ticked_nos = [int(no) for no in all_ticked_nos.split(",") if no] if all_ticked_nos else []

            if not ticked_nos:
                messages.error(request, "No shipments selected for export.")
                return pr()

            try:
                # === NEW: Check if client sent exact order ===
                order_ids_str = request.POST.get("export_order_ids", "")
                if order_ids_str:
                    try:
                        ordered_ids = [int(x) for x in order_ids_str.split(",") if x]
                        logger.info(f"mainView1: Using client-provided order: {len(ordered_ids)} IDs")
                        # Fetch in exact order using CASE + FIELD trick
                        from django.db.models import Case, When, Value, IntegerField
                        preserved_order = Case(
                            *[When(number=id, then=Value(i)) for i, id in enumerate(ordered_ids)],
                            default=Value(len(ordered_ids)),
                            output_field=IntegerField()
                        )
                        shipments = Shipment.objects.filter(number__in=ordered_ids).annotate(
                            _order=preserved_order
                        ).order_by('_order')
                    except Exception as e:
                        logger.warning(f"Failed to apply client order: {e}. Falling back to default.")
                        shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')
                else:
                    # Fallback: default order
                    shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')

                context["allTickedShipments"] = list(shipments)

                if not context["allTickedShipments"]:
                    messages.error(request, "No shipments found for export.")
                    return pr()

                response = paginate_shipment_Excel(request, context, "allTickedShipments")
                messages.success(request, f"{len(context['allTickedShipments'])} shipments exported in current screen order.")

                # Clear selections
                request.session["shipmentTickedNos"] = []
                request.session["shipmentTicked"] = {}
                request.session["shipment0Ticked"] = {}
                request.session.modified = True
                CONTEXT["shipmentTickedNos"] = []

                return response

            except Exception as e:
                logger.error(f"mainView1: Export error: {str(e)}", exc_info=True)
                messages.error(request, "Failed to export shipments.")
                return pr()

        # Handle page navigation or form submission
        shipments = Shipment.objects.all().order_by("-number")
        paginator = Paginator(shipments, SHIPMENTS_PER_PAGE)
        pagination = paginator.get_page(page_num)
        context['totalResults'] = len(shipments)
        context['shipmentPage'] = pagination
        page_num_total = paginator.num_pages
        tick_keyword, untick_keyword = "pageSticked", "page0Sticked"

        logger.info(f"mainView1: Session after POST: {request.session.get('shipmentTickedNos', [])}")

        if request.POST.get("statusS") == "nothing" or "pageSticked" in request.POST:
            logger.info("mainView1: Processing statusS=nothing or pageSticked")
            list_ticked = request.POST.get(tick_keyword, "")
            list_unticked = request.POST.get(untick_keyword, "")
            IDs_ticked = [int(id) for id in list_ticked.split(",") if id] if list_ticked else []
            IDs_unticked = [int(id) for id in list_unticked.split(",") if id] if list_unticked else []

            request.session["shipment0Ticked"][str(page_num)] = IDs_unticked
            request.session["shipmentTicked"][str(page_num)] = [
                id_ticked for id_ticked in IDs_ticked if id_ticked not in IDs_unticked
            ]
            total_ticked = []
            for page in range(1, page_num_total + 1):
                total_ticked.extend(request.session["shipmentTicked"].get(str(page), []))
            request.session["shipmentTickedNos"] = list(set(total_ticked))
            CONTEXT["shipmentTickedNos"] = request.session["shipmentTickedNos"]
            request.session.modified = True
            logger.info(f"mainView1: Updated shipmentTickedNos: {request.session['shipmentTickedNos']}")

        if "addShipment" in request.POST:
            context_ = register_shipment(request, context, form_keyword="shipmentRegForm")
            context.update(context_)
            logger.info("mainView1: Redirecting after addShipment")
            shipments = Shipment.objects.all().order_by("-number")
            paginator = Paginator(shipments, SHIPMENTS_PER_PAGE)
            page_num = request.POST.get('page')
            pagination = paginator.get_page(page_num)
            context['totalResults'] = len(shipments)
            context['shipmentPage'] = pagination
            return pr()
            # (Preserved via PR helper)

        elif "addShipmentM" in request.POST:
            # Note: Do NOT perform heavy queries here (like filtering/paginating all shipments)
            # The focus is on the registration itself.
            context_ = register_shipment(request, context, form_keyword="shipmentRegFormM")
            context.update(context_)
            
            # --- Check for errors before redirecting ---
            # If the registration function adds form errors to the context, 
            # we must render the original page to show the errors.
            # Assuming 'register_shipment' modifies context to include errors if validation fails.
            if context.get('shipmentRegFormM') and context['shipmentRegFormM'].errors:
                messages.error(request, "Please correct the errors below to add the shipment.")
                # Since we have errors, we must let mainView1 continue to render 
                # the mobile page with the form and errors.
                # Remove the unnecessary pagination logic here, it will be done on render.
                # return redirect('mainPageMobile1') # Instead of redirect, let the view render
                pass # Let the function finish and render mainPageMobile1 with errors
            else:
                # --- SUCCESS: Redirect to the FAST Success page ---
                messages.success(request, "New shipment added successfully!")
                return redirect('shipmentAddedSuccessM') # <--- NEW FAST REDIRECT

        elif "adjustShipment" in request.POST:
            context_ = adjust_shipment(request, context, form_keyword="shipmentRegForm")
            context.update(context_)
            return pr()

        elif "modifyShipment" in request.POST:
            context_ = paginate_shipment_modify(request, context, form_keyword="shipmentModForm")
            context.update(context_)
            
            # Clear ticked selections after modify (your original logic)
            request.session["shipmentTickedNos"] = []
            request.session["shipmentTicked"] = {}
            request.session["shipment0Ticked"] = {}
            request.session.modified = True
            CONTEXT["shipmentTickedNos"] = []
            reset_paginated_Sticks(context, max_page_range=800)
            
            messages.success(request, "Shipments updated successfully!")
            
            # === FIX: Redirect back to the same filtered/paginated/sorted page ===
            query_string = request.GET.urlencode()
            return redirect(f'/main1/?{query_string}')  # or use reverse('main1') + '?' + query_string
        #In mainView1, add this elif block after your Excel export
        elif "exportPdfShipment" in request.POST:
            logger.info("mainView1: ExportPdfShipment button clicked")

            all_ticked_nos = request.POST.get("allTickedNos", "")
            ticked_nos = [int(no) for no in all_ticked_nos.split(",") if no] if all_ticked_nos else []

            if not ticked_nos:
                messages.error(request, "No shipments selected for PDF export.")
                return pr()

            try:
                # === NEW: Check if client sent exact visual order ===
                order_ids_str = request.POST.get("export_order_ids", "")
                if order_ids_str:
                    try:
                        ordered_ids = [int(x) for x in order_ids_str.split(",") if x]
                        logger.info(f"mainView1: PDF using client order: {len(ordered_ids)} shipments")
                        from django.db.models import Case, When, Value, IntegerField
                        preserved_order = Case(
                            *[When(number=id, then=Value(i)) for i, id in enumerate(ordered_ids)],
                            default=Value(len(ordered_ids)),
                            output_field=IntegerField()
                        )
                        shipments = Shipment.objects.filter(number__in=ordered_ids).annotate(
                            _order=preserved_order
                        ).order_by('_order')
                    except Exception as e:
                        logger.warning(f"PDF: Failed to apply client order ({e}). Using default.")
                        shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')
                else:
                    # Fallback order
                    shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')

                context["allTickedShipments"] = list(shipments)

                if not context["allTickedShipments"]:
                    messages.error(request, "No shipments found for PDF export.")
                    return pr()

                response = paginate_shipment_PDF(request, context, "allTickedShipments")
                messages.success(request, f"PDF generated for {len(context['allTickedShipments'])} shipments in current screen order.")

                return response

            except Exception as e:
                logger.error(f"mainView1: PDF export error: {str(e)}", exc_info=True)
                messages.error(request, "Failed to generate PDF.")
                return pr()
            
        elif "deleteShipment" in request.POST:
            logger.info("mainView1: DeleteShipment button clicked")
            all_ticked_nos = request.POST.get("allTickedNos", "")
            ticked_nos = [int(no) for no in all_ticked_nos.split(",") if no] if all_ticked_nos else []
            logger.info(f"mainView1: Selected shipment numbers for deletion: {len(ticked_nos)} IDs: {ticked_nos}")

            if not ticked_nos:
                logger.warning("mainView1: No shipments selected for deletion")
                messages.error(request, "No shipments selected for deletion.")
                return pr()

            try:
                # Verify which shipment IDs exist
                existing_shipments = Shipment.objects.filter(number__in=ticked_nos).values_list('number', flat=True)
                existing_ticked_nos = set(existing_shipments)
                missing_nos = set(ticked_nos) - existing_ticked_nos
                if missing_nos:
                    logger.warning(f"mainView1: Some shipment IDs not found: {missing_nos}")

                # Delete shipments and get actual count
                deleted_count = Shipment.objects.filter(number__in=ticked_nos).delete()[0]
                logger.info(f"mainView1: Deleted {deleted_count} shipments out of {len(ticked_nos)} requested")

                # Store deleted count in session
                request.session["deleted_count"] = deleted_count
                request.session.modified = True

                # Clear selections
                request.session["shipmentTickedNos"] = []
                request.session["shipmentTicked"] = {}
                request.session["shipment0Ticked"] = {}
                request.session.modified = True
                CONTEXT["shipmentTickedNos"] = []

                # Force session save
                request.session.save()
                logger.info(f"mainView1: Session saved with deleted_count={deleted_count}, shipmentTickedNos={request.session['shipmentTickedNos']}")

                # Add success message
                messages.success(request, f"{deleted_count} shipment(s) were successfully deleted.")
                if missing_nos:
                    messages.warning(request, f"Some shipments could not be deleted (IDs not found: {missing_nos}).")

                return pr()
            except Exception as e:
                logger.error(f"mainView1: Delete error: {str(e)}")
                messages.error(request, f"Failed to delete shipments: {str(e)}")
                return pr()

        elif "uploadExcel" in request.POST:
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                messages.error(request, "No Excel file uploaded.")
                return pr()

            # Define constants
            SM = 50
            LG = 200
            MD = 50
            TEXT_MAX = 1000

            def parse_date_field(raw_value, field_name, index):
                # ... (parse_date_field implementation remains the same) ...
                if pd.isna(raw_value) or str(raw_value).strip() == '':
                    return None
                try:
                    date_obj = pd.to_datetime(raw_value, errors='coerce')
                    if pd.isna(date_obj):
                        return None
                    result = date_obj.strftime('%Y-%m-%d')
                    datetime.strptime(result, '%Y-%m-%d')
                    return result
                except (ValueError, TypeError):
                    return None

            try:
                # 1. Read Excel and Normalize Columns (as previously agreed)
                df = pd.read_excel(
                    excel_file,
                    engine='openpyxl',
                    dtype={
                        'SHIPMENT ID': str, 'COMPANY': str, 'VESSEL': str, 'DOCS': str,
                        'ORDER.NO': str, 'SUPPLIER': str, 'C.PACKING': str, 'QTY': str,
                        'UNIT': str, 'SIZE': str, 'WEIGHT': str, 'IN DATE': str,
                        'W/H': str, 'BY': str, 'IMP.BL': str, 'EXP.BL': str,
                        'PORT': str, 'ONBOARD DATE': str, 'REMARK': str, 'DIVISION': str,
                        'STATUS': str
                    }
                )

                # Robust Normalize column names: remove BOM/unicode slashes and any non-alphanumeric
                orig_cols = list(df.columns)
                normalized = []
                for col in orig_cols:
                    c = col if isinstance(col, str) else str(col)
                    # remove BOM and common unicode slash variants
                    c = c.replace('\ufeff', '').replace('\u200b', '')
                    c = c.replace('／', '/').replace('‒', '-').replace('–', '-').replace('—', '-')
                    c = c.replace('\\', '/').replace('\u2215', '/')
                    # Keep only letters and digits
                    c = re.sub(r'[^A-Z0-9]', '', c.upper().strip())
                    normalized.append(c)
                df.columns = normalized

                # If the warehouse column exists with variants (e.g. 'WH', 'WH1', 'WH.1'), map the first candidate to 'WH'
                wh_candidates = [c for c in df.columns if c.startswith('WH')]
                if wh_candidates:
                    first = wh_candidates[0]
                    if first != 'WH':
                        # rename the first candidate to canonical 'WH'
                        df.rename(columns={first: 'WH'}, inplace=True)

                text_columns = [
                    'SHIPMENTID', 'COMPANY', 'VESSEL', 'DOCS', 'ORDERNO', 'SUPPLIER',
                    'CPACKING', 'QTY', 'UNIT', 'SIZE', 'WEIGHT', 'WH',
                    'BY', 'IMPBL', 'EXPBL', 'PORT', 'REMARK', 'DIVISION', 'STATUS'
                ]
                for col in text_columns:
                    if col in df.columns:
                        df[col] = df[col].fillna('')

                if df.empty:
                    messages.error(request, "Excel file is empty.")
                    return pr()

                errors = []
                valid_rows = []

                # List to track objects for bulk operations
                to_create = []
                to_update = []

                for index, row in df.iterrows():
                    row_errors = []
                    excel_row_number = index + 2

                    # 2. Data Extraction
                    shipment_id = str(row.get('SHIPMENTID', '')).strip()[:SM]
                    company = str(row.get('COMPANY', '')).strip()[:LG]
                    c_packing = str(row.get('CPACKING', '')).strip()[:SM]
                    vessel = str(row.get('VESSEL', '')).strip()[:LG]

                    in_date_str = parse_date_field(row.get('INDATE', row.get('IN', '')), 'INDATE', index)
                    in_date_for_id = datetime.strptime(in_date_str, '%Y-%m-%d') if in_date_str else datetime.now().date()
                    in_date_db = in_date_for_id.strftime('%Y-%m-%d') if in_date_str else None
                    out_date = parse_date_field(row.get('ONBOARDDATE', ''), 'ONBOARDDATE', index)

                    quanty = str(row.get('QTY', '')).strip()[:SM]
                    weight = str(row.get('WEIGHT', '')).strip()[:LG]
                    docs = str(row.get('DOCS', '')).strip()[:TEXT_MAX]
                    remark = str(row.get('REMARK', '')).strip()[:TEXT_MAX]
                    order_no = str(row.get('ORDERNO', '')).strip()[:TEXT_MAX]
                    supplier = str(row.get('SUPPLIER', '')).strip()[:TEXT_MAX]
                    division = str(row.get('DIVISION', '')).strip()[:SM]
                    unit = str(row.get('UNIT', '')).strip()[:SM]
                    size = str(row.get('SIZE', '')).strip()[:LG]
                    warehouse = str(row.get('WH', '')).strip()[:LG]
                    by_value = str(row.get('BY', '')).strip()[:MD]
                    imp_bl = str(row.get('IMPBL', '')).strip()[:LG]
                    exp_bl = str(row.get('EXPBL', '')).strip()[:LG]
                    port = str(row.get('PORT', '')).strip()[:LG]
                    flag_status = str(row.get('STATUS', '')).strip()[:SM]

                    # 3. Mandatory Field Check
                    if not company:
                        row_errors.append("COMPANY cannot be empty.")
                    if c_packing and c_packing not in PRELIST_DATA.get("cpacking", ["YES", "NO"]):
                        row_errors.append(f"CPACKING '{c_packing}' must be one of: {PRELIST_DATA.get('cpacking', ['YES', 'NO'])}")

                    if row_errors:
                        errors.append({"row": excel_row_number, "errors": row_errors})
                        continue

                    # 4. Update/Insert Decision
                    shipment = None
                    is_new = False

                    if shipment_id:
                        # Case A: ID is provided -> Try to Update
                        try:
                            shipment = Shipment.objects.get(shipment_id=shipment_id)
                        except Shipment.DoesNotExist:
                            is_new = True
                            shipment = Shipment(shipment_id=shipment_id)
                    else:
                        # Case B: ID is NOT provided -> Generate New ID and Insert
                        is_new = True
                        attempt = 0
                        max_attempts = 10
                        while attempt < max_attempts:
                            shipment_id_new = generate_shipment_id(company, vessel or 'XX', in_date_for_id)
                            if not Shipment.objects.filter(shipment_id=shipment_id_new).exists():
                                shipment_id = shipment_id_new
                                break
                            attempt += 1
                        if attempt >= max_attempts:
                            row_errors.append(f"Could not generate unique SHIPMENTID for row {excel_row_number}")
                            errors.append({"row": excel_row_number, "errors": row_errors})
                            continue

                        shipment = Shipment(shipment_id=shipment_id)

                    # 5. Set insert/correct org and update all fields
                    current_user_id = str(request.user.userID) if request.user.is_authenticated else None

                    if is_new:
                        shipment.insert_org = current_user_id
                        # Correct_org is left blank/default
                    else:
                        shipment.correct_org = current_user_id

                    # Set the rest of the fields
                    shipment.company = company
                    shipment.vessel = vessel
                    shipment.docs = docs
                    shipment.Order_No = order_no
                    shipment.supplier = supplier
                    shipment.division = division
                    shipment.c_packing = c_packing
                    shipment.quanty = quanty
                    shipment.unit = unit
                    shipment.size = size
                    shipment.weight = weight
                    shipment.in_date = in_date_db
                    shipment.warehouse = warehouse
                    shipment.by = by_value
                    shipment.IMP_BL = imp_bl
                    shipment.EXP_BL = exp_bl
                    shipment.port = port
                    shipment.out_date = out_date
                    shipment.remark = remark
                    shipment.flag_status = flag_status or 'BLANK'
                    shipment.colordiv = {'B': 'red', 'L': 'blue'}.get(division, 'black')

                    # 6. Add to appropriate list
                    if is_new:
                        to_create.append(shipment)
                    else:
                        # Existing objects will have a primary key (pk) from the .get() call
                        to_update.append(shipment)

                # 7. Error Handling and Bulk Operations
                if errors:
                    # Save errors to session for later display/download
                    request.session['excel_errors'] = errors
                    request.session.modified = True

                    # Log full error details (for server logs)
                    logger.error("Excel import errors: %s", errors)

                    # Also print to stdout if you want immediate console output (optional)
                    print("Excel import errors:", errors)

                    # Build a short, user-friendly summary for Django messages (limit length)
                    summary_items = []
                    for item in errors[:5]:  # show up to 5 rows in the message
                        row = item.get("row", "?")
                        errs = item.get("errors", [])
                        summary_items.append(f"Row {row}: {'; '.join(errs)}")
                    summary = " | ".join(summary_items)
                    if len(errors) > 5:
                        summary += f" (and {len(errors) - 5} more rows)"

                    messages.error(request, f"Found {len(errors)} errors in the Excel file: {summary}")
                    return pr()

                try:
                    with transaction.atomic():
                        if to_create:
                            Shipment.objects.bulk_create(to_create)

                        if to_update:
                            update_fields = [
                                'company', 'vessel', 'docs', 'Order_No', 'supplier', 'division',
                                'c_packing', 'quanty', 'unit', 'size', 'weight', 'in_date',
                                'warehouse', 'by', 'IMP_BL', 'EXP_BL', 'port', 'out_date',
                                'remark', 'flag_status', 'colordiv', 'correct_org'
                            ]
                            Shipment.objects.bulk_update(to_update, update_fields)

                    uploaded_count = len(to_create) + len(to_update)
                    messages.success(request, f"Successfully processed {uploaded_count} shipments from Excel. ({len(to_create)} created, {len(to_update)} updated)")
                    return pr()
                except IntegrityError as e:
                    messages.error(request, f"Failed to save shipments due to database error: {str(e)}")
                    return pr()

            except Exception as e:
                messages.error(request, f"An unexpected error occurred during file processing: {str(e)}")
                return pr()

        
        # Display deletion message if present (fallback for session issues)
        if "deleted_count" in request.session:
            deleted_count = request.session.pop("deleted_count")
            request.session.modified = True
            request.session.save()
            messages.success(request, f"{deleted_count} shipment(s) were successfully deleted.")

    # 1. Recalculate the Grand Total (unfiltered count)
    context["totalShipments"] = Shipment.objects.all().count() 

    # 2. Update allTickedShipments (this logic was correct and needed)
    context["allTickedNos"] = request.session["shipmentTickedNos"]
    try:
        context["allTickedShipments"] = list(Shipment.objects.filter(number__in=context["allTickedNos"]))
    except Exception as e:
        logger.error(f"mainView1: Error fetching allTickedShipments for render: {e}")
        context["allTickedShipments"] = []

    response = render(request, "mainPage1.html" if not useragent.is_mobile else "mainPageMobile1.html", context)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

def mainShipmentSuccessM(request):
    """
    Minimal view to display success message and automatically redirect
    to avoid slow reload after form submission.
    """
    # This view performs NO heavy database queries, ensuring a fast load time.
    return render(request, "shipmentSuccessMobile.html", {}) 

def pageSelect(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    action = data.get('action')

    if action == 'get':
        ticked_nos = request.session.get("shipmentTickedNos", [])
        total_count = len(ticked_nos)
        # Verify ticked_nos against database
        existing_nos = Shipment.objects.filter(number__in=ticked_nos).values_list('number', flat=True)
        missing_nos = set(ticked_nos) - set(existing_nos)
        if missing_nos:
            logger.warning(f"pageSelect: Ticked shipment IDs not found in database: {missing_nos}")
        logger.info(f"pageSelect: Returning tickedNos={ticked_nos}, totalCount={total_count}")
        return JsonResponse({
            'tickedNos': ticked_nos,
            'totalCount': total_count,
            'missingNos': list(missing_nos)  # For debugging
        })

    elif action == 'update':
        ticked_nos = data.get('tickedNos', [])
        unticked_nos = data.get('untickedNos', [])
        current_ticked = set(request.session.get('shipmentTickedNos', []))
        current_ticked.update(ticked_nos)
        current_ticked.difference_update(unticked_nos)
        request.session['shipmentTickedNos'] = list(current_ticked)
        request.session.modified = True
        # Optionally update per-page ticked (but since global is source of truth, maybe not needed)
        return JsonResponse({'status': 'success'})

    elif action == 'select_all':
        # Recompute filtered shipments (applies user-specific filters)
        filter_show = filter_shipment(request, "shipmentFilterForm", "shipmentPage", "shipmentResults")
        ticked_nos = list(filter_show["shipmentResults"].values_list('number', flat=True))
        request.session["shipmentTickedNos"] = ticked_nos
        request.session["shipmentTicked"] = {}  # Reset per-page data
        request.session["shipment0Ticked"] = {}
        request.session.modified = True
        return JsonResponse({
            'status': 'success',
            'tickedNos': ticked_nos,
            'totalCount': len(ticked_nos)  # Since all are selected
        })

    elif action == 'clear':
        request.session["shipmentTickedNos"] = []
        request.session["shipmentTicked"] = {}
        request.session["shipment0Ticked"] = {}
        request.session.modified = True
        # Recompute filtered total for response
        filter_show = filter_shipment(request, "shipmentFilterForm", "shipmentPage", "shipmentResults")
        total_count = len(filter_show["shipmentResults"])
        return JsonResponse({
            'status': 'success',
            'tickedNos': [],
            'totalCount': total_count
        })

    return JsonResponse({'error': 'Invalid action'}, status=400)

def mainDownloaded1(request):
    return render(request, "shipmentDownloaded1.html", {})

def mainUpdated1(request):
    return render(request, "shipmentUpdated1.html", {})

def mainView2(request):
    useragent = get_user_agent(request)
    context = {k: CONTEXT[k] for k in CONTEXT.keys()}
    context["roleLogin"] = "staff"
    context["shipmentRegForm"] = ShipmentRegistrationForm()
    context["shipmentRegFormM"] = ShipmentRegistrationForm()
    context["shipmentModForm"] = ShipmentModificationForm()
    context["pending_form"] = PendingShipmentForm()  # Add the form

    # Load suppliers from database
    suppliers = list(Supplier.objects.values_list('name', flat=True).order_by('name'))
    context["prelistSuppliers"] = json.dumps(suppliers, ensure_ascii=False)  # JSON string
    context["suppliers_list"] = suppliers  # Python list

    # Filter vessels based on user type

    # current_user = request.user
    # if current_user.isOpr:
    #     vessel_list = []
    #     all_accounts_with_vessels = Account.objects.all().filter(vesselList__gt='')
    #     for account in all_accounts_with_vessels:
    #         account_vessels = account.vesselList.split(',')
    #         for vessel in account_vessels:
    #             vessel_list.append(vessel)
    # elif current_user.isCpn and current_user.vesselList:
    #     vessel_list = current_user.vesselList.split(',')
    # else:
    #     vessel_list = []

    company_list = []
    if hasattr(request.user, 'isCpn') and request.user.isCpn:  # If the user is a company
        company_list = [request.user.companyName]  # Only the logged-in company
    elif hasattr(request.user, 'isOpr') and request.user.isOpr:  # If the user is an operator
        company_list = COMPANY_LIST

    context['company_list'] = company_list  # Pass the company list to the template

    # Pass the supplier name if the user is a supplier
    supplier_name = None
    if hasattr(request.user, 'isSpl') and request.user.isSpl:  # Check if the user is a supplier
        supplier_name = request.user.supplierName  # Assuming the supplier's name is stored in the username field
    context['supplier_name'] = supplier_name

    vessel_list = []
    if hasattr(request.user, 'isCpn') and request.user.isCpn:  # If the user is a company
        if hasattr(request.user, 'vesselList') and request.user.vesselList:
            vessel_list = request.user.vesselList.split(',')  # Company-specific vessels
    elif hasattr(request.user, 'isSpl') and request.user.isSpl:  # If the user is a supplier
        # Add supplier-specific logic here if needed
        vessel_list = []  # Example: No vessels for suppliers
    else:
        # If the user is neither a company nor a supplier, show all vessels
        all_accounts_with_vessels = Account.objects.all().filter(vesselList__gt='')
        for account in all_accounts_with_vessels:
            account_vessels = account.vesselList.split(',')
            for vessel in account_vessels:
                vessel_list.append(vessel)

    context['filtered_vessels'] = vessel_list  # Pass the filtered vessel list to the template

    filter_show = filter_shipment(request, "shipmentFilterForm", "shipmentPage", "shipmentResults")
    context['totalResults'] = len(filter_show["shipmentResults"])
    context.update(filter_show)
    page_num = filter_show["page_num"]
    page_num_total = filter_show["page_num_total"]

    # === ADD TOGGLE ORDER COMPUTATION FOR EACH COLUMN ===
    current_sort = context.get('current_sort')
    current_order = context.get('current_order', 'asc')

    # Compute next order for each sortable field (add all your columns here)
    context['shipment_id_order'] = 'desc' if current_sort == 'shipment_id' and current_order == 'asc' else 'asc'
    context['company_order'] = 'desc' if current_sort == 'company' and current_order == 'asc' else 'asc'
    context['vessel_order'] = 'desc' if current_sort == 'vessel' and current_order == 'asc' else 'asc'
    context['supplier_order'] = 'desc' if current_sort == 'supplier' and current_order == 'asc' else 'asc'
    context['quanty_order'] = 'desc' if current_sort == 'quanty' and current_order == 'asc' else 'asc'
    context['c_packing_order'] = 'desc' if current_sort == 'c_packing' and current_order == 'asc' else 'asc'
    context['weight_order'] = 'desc' if current_sort == 'weight' and current_order == 'asc' else 'asc'
    context['unit_order'] = 'desc' if current_sort == 'unit' and current_order == 'asc' else 'asc'
    context['size_order'] = 'desc' if current_sort == 'size' and current_order == 'asc' else 'asc'
    context['docs_order'] = 'desc' if current_sort == 'docs' and current_order == 'asc' else 'asc'
    context['in_date_order'] = 'desc' if current_sort == 'in_date' and current_order == 'asc' else 'asc'
    context['warehouse_order'] = 'desc' if current_sort == 'warehouse' and current_order == 'asc' else 'asc'
    context['by_order'] = 'desc' if current_sort == 'by' and current_order == 'asc' else 'asc'
    context['IMP_BL_order'] = 'desc' if current_sort == 'IMP_BL' and current_order == 'asc' else 'asc'
    context['port_order'] = 'desc' if current_sort == 'port' and current_order == 'asc' else 'asc'
    context['out_date_order'] = 'desc' if current_sort == 'out_date' and current_order == 'asc' else 'asc'
    context['remark_order'] = 'desc' if current_sort == 'remark' and current_order == 'asc' else 'asc'
    context['EXP_BL_order'] = 'desc' if current_sort == 'EXP_BL' and current_order == 'asc' else 'asc'
    context['flag_status_order'] = 'desc' if current_sort == 'flag_status' and current_order == 'asc' else 'asc'
    context['insert_org_order'] = 'desc' if current_sort == 'insert_org' and current_order == 'asc' else 'asc'
    context['correct_org_order'] = 'desc' if current_sort == 'correct_org' and current_order == 'asc' else 'asc'
    context['Order_No_order'] = 'desc' if current_sort == 'Order_No' and current_order == 'asc' else 'asc'
    # Add any other sortable fields similarly

    # Initialize session data if not present
    if "shipmentTickedNos" not in request.session:
        request.session["shipmentTickedNos"] = []
        request.session.modified = True
    if "shipmentTicked" not in request.session:
        request.session["shipmentTicked"] = {}
        request.session.modified = True
    if "shipment0Ticked" not in request.session:
        request.session["shipment0Ticked"] = {}
        request.session.modified = True

    # Sync CONTEXT with session
    CONTEXT["shipmentTickedNos"] = request.session["shipmentTickedNos"]
    logger.info(f"mainView1: Session shipmentTickedNos: {request.session['shipmentTickedNos']}")

    # Set allTickedNos from session
    context["allTickedNos"] = request.session["shipmentTickedNos"]
    if not context["allTickedNos"]:
        context["allTickedShipments"] = []
    else:
        try:
            ticked_nos = [int(no) for no in context["allTickedNos"]]
            shipments = Shipment.objects.filter(number__in=ticked_nos)
            context["allTickedShipments"] = list(shipments)
            logger.info(f"mainView1: Retrieved {len(context['allTickedShipments'])} allTickedShipments for {len(ticked_nos)} allTickedNos")
        except Exception as e:
            logger.error(f"mainView1: Error fetching allTickedShipments: {e}")
            context["allTickedShipments"] = []

    if request.method == "POST":
        logger.info("mainView1: Received POST request")
        logger.debug(f"mainView1: POST data: {request.POST}")
        logger.info(f"mainView1: Session before POST: {request.session.get('shipmentTickedNos', [])}")

        # Handle AJAX checkbox updates
        if "update_selection" in request.POST:
            shipment_number = request.POST.get("shipment_number")
            is_checked = request.POST.get("is_checked") == "true"
            current_selections = request.session.get("shipmentTickedNos", [])

            try:
                shipment_number = int(shipment_number)
                if is_checked and shipment_number not in current_selections:
                    current_selections.append(shipment_number)
                elif not is_checked and shipment_number in current_selections:
                    current_selections.remove(shipment_number)
                request.session["shipmentTickedNos"] = list(set(current_selections))
                request.session.modified = True

                # Update page-specific selections
                page_num = request.POST.get("page", str(page_num))
                list_ticked = request.POST.get("pageSticked", "")
                list_unticked = request.POST.get("page0Sticked", "")
                ticked_ids = [int(id) for id in list_ticked.split(",") if id] if list_ticked else []
                unticked_ids = [int(id) for id in list_unticked.split(",") if id] if list_unticked else []
                request.session["shipmentTicked"][page_num] = ticked_ids
                request.session["shipment0Ticked"][page_num] = unticked_ids
                request.session.modified = True

                return JsonResponse({"status": "success"})
            except (ValueError, TypeError) as e:
                logger.error(f"mainView1: Error updating selection: {e}")
                return JsonResponse({"status": "error", "message": str(e)}, status=400)

        if "exportExcelShipment" in request.POST:
            logger.info("mainView2: ExportExcelShipment button clicked")

            all_ticked_nos = request.POST.get("allTickedNos", "")
            ticked_nos = [int(no) for no in all_ticked_nos.split(",") if no] if all_ticked_nos else []

            if not ticked_nos:
                messages.error(request, "No shipments selected for export.")
                return redirect(request.path)  # or your pr() equivalent

            try:
                # Use client-provided exact order if available
                order_ids_str = request.POST.get("export_order_ids", "")
                if order_ids_str:
                    try:
                        ordered_ids = [int(x) for x in order_ids_str.split(",") if x]
                        logger.info(f"mainView2: Using client visual order: {len(ordered_ids)} items")
                        from django.db.models import Case, When, Value, IntegerField
                        preserved_order = Case(
                            *[When(number=id, then=Value(i)) for i, id in enumerate(ordered_ids)],
                            default=Value(len(ordered_ids)),
                            output_field=IntegerField()
                        )
                        shipments = Shipment.objects.filter(number__in=ordered_ids).annotate(
                            _order=preserved_order
                        ).order_by('_order')
                    except Exception as e:
                        logger.warning(f"mainView2: Failed to preserve order: {e}")
                        shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')
                else:
                    shipments = Shipment.objects.filter(number__in=ticked_nos).order_by('-in_date', '-number')

                context["allTickedShipments"] = list(shipments)

                if not context["allTickedShipments"]:
                    messages.error(request, "No shipments found for export.")
                    return redirect(request.path)

                response = paginate_shipment_Excel(request, context, "allTickedShipments")
                messages.success(request, f"{len(context['allTickedShipments'])} shipments exported in current screen order.")

                # Clear selections
                request.session["shipmentTickedNos"] = []
                request.session["shipmentTicked"] = {}
                request.session["shipment0Ticked"] = {}
                request.session.modified = True
                CONTEXT["shipmentTickedNos"] = []

                return response

            except Exception as e:
                logger.error(f"mainView2: Export error: {str(e)}", exc_info=True)
                messages.error(request, "Failed to export shipments.")
                return redirect(request.path)
            
        if "add_pending_shipment" in request.POST:
                form = PendingShipmentForm(request.POST)
                if form.is_valid():
                    pending = form.save(commit=False)
                    pending.submitted_by = request.user
                    pending.save()
                    messages.success(request, "Shipment submitted for approval. Awaiting staff review.")
                    return redirect('mainPage2')
                else:
                    messages.error(request, "Invalid form data. Please check and try again.")
                    context["pending_form"] = form

    response = render(request, "mainPage2.html" if not useragent.is_mobile else "mainPageMobile2.html", context)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

def mainDownloaded2(request):
    return render(request, "shipmentDownloaded2.html", {})

# In shipments/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
import subprocess

def downloadShipmentPdf(request, shipment_id):
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
        movements = shipment.movements.all()
        context = {
            'shipment': shipment,
            'movements': movements,
        }
        # Render LaTeX template
        latex_content = render_to_string('shipment_summary.tex', context)
        # Save LaTeX file temporarily
        temp_dir = settings.MEDIA_ROOT  # Ensure MEDIA_ROOT is set in settings.py
        os.makedirs(temp_dir, exist_ok=True)
        tex_file = os.path.join(temp_dir, f'shipment_{shipment_id}.tex')
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        # Compile LaTeX to PDF using latexmk
        subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', tex_file], cwd=temp_dir, check=True)
        pdf_file = os.path.join(temp_dir, f'shipment_{shipment_id}.pdf')
        # Read PDF and serve
        with open(pdf_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="shipment_{shipment_id}.pdf"'
        # Clean up temporary files
        for ext in ['tex', 'pdf', 'aux', 'log', 'fls', 'fdb_latexmk']:
            try:
                os.remove(os.path.join(temp_dir, f'shipment_{shipment_id}.{ext}'))
            except FileNotFoundError:
                pass
        return response
    except Shipment.DoesNotExist:
        messages.error(request, f"Shipment {shipment_id} not found.")
        return redirect('mainPage1')
    except subprocess.CalledProcessError:
        messages.error(request, "Failed to generate PDF.")
        return redirect('shipmentTrackingView', shipment_id=shipment_id)

def customerTracking(request):
    context = {'shipment_id': ''}
    if 'shipment_id' in request.GET:
        shipment_id = request.GET['shipment_id'].strip()
        context['shipment_id'] = shipment_id
        try:
            shipment = Shipment.objects.get(shipment_id=shipment_id)
            movements = ShipmentMovement.objects.filter(shipment=shipment).order_by('timestamp')
            evaluation_exists = ShipmentEvaluation.objects.filter(shipment=shipment).exists()
            existing_evaluation = ShipmentEvaluation.objects.filter(shipment=shipment).first()
            context.update({
                'shipment': shipment,
                'movements': movements,
                'evaluation_exists': evaluation_exists,
                'existing_evaluation': existing_evaluation,
            })
        except Shipment.DoesNotExist:
            context['error'] = 'Shipment ID not found.'
    return render(request, 'customerTracking.html', context)


@login_required
def updateShipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        # Get form data, treating empty strings as None
        location = request.POST.get('location', '').strip() or None
        warehouse = request.POST.get('warehouse', '').strip() or None
        transport_mode = request.POST.get('transport_mode', '').strip()
        remark = request.POST.get('remark', '').strip() or None

        # Transport mode is a required field. If it's empty, block the submission.
        if not transport_mode:
            messages.error(request, 'Transport Mode is required.')
            logger.error(f"Validation failed for shipment {shipment_id}: Transport Mode missing")
            return redirect('shipmentTrackingView', shipment_id=shipment_id)

        # Check for changes in location and warehouse.
        location_changed = (location != shipment.location)
        warehouse_changed = (warehouse != shipment.warehouse)

        # If no changes were made to either field, inform the user and redirect without creating a new row
        if not location_changed and not warehouse_changed:
            messages.info(request, 'No changes detected in Location or Warehouse.')
            return redirect('shipmentTrackingView', shipment_id=shipment_id)

        # Update the shipment object with new values
        shipment.location = location
        shipment.warehouse = warehouse
        shipment.save()

        # Determine the single movement type
        if location_changed and warehouse_changed:
            movement_type = 'LOCATION_WAREHOUSE_UPDATE'
        elif location_changed:
            movement_type = 'LOCATION_UPDATE'
        elif warehouse_changed:
            movement_type = 'WAREHOUSE_UPDATE'
        else:
            movement_type = 'OTHER' # Fallback

        # Get the latest movement to retain unchanged fields
        latest_movement = shipment.movements.order_by('-timestamp').first()

        # Create a single ShipmentMovement record
        ShipmentMovement.objects.create(
            shipment=shipment,
            movement_type=movement_type,
            location=location,
            warehouse=warehouse,
            transport_mode=transport_mode,
            changed_by=request.user,
            remark=remark,
            flag_status=latest_movement.flag_status if latest_movement else shipment.flag_status,
            in_date=latest_movement.in_date if latest_movement else None,
            out_date=latest_movement.out_date if latest_movement else None,
        )

        messages.success(request, 'Shipment information updated successfully.')
        return redirect('shipmentTrackingView', shipment_id=shipment_id)

    logger.warning(f"Invalid request method for updateShipment: {request.method}")
    return redirect('shipmentTrackingView', shipment_id=shipment_id)

@csrf_exempt
def submit_evaluation(request):
    if request.method == 'POST':
        try:
            data = request.POST
            shipment_id = data.get('shipment_id')
            rating = int(data.get('rating'))
            comment = data.get('comment', '').strip()

            if not (1 <= rating <= 5):
                return JsonResponse({'error': 'Invalid rating.'}, status=400)

            shipment = Shipment.objects.get(shipment_id=shipment_id)
            if ShipmentEvaluation.objects.filter(shipment=shipment).exists():
                return JsonResponse({'error': 'Evaluation already submitted.'}, status=400)

            evaluation = ShipmentEvaluation.objects.create(
                shipment=shipment,
                rating=rating,
                comment=comment
            )
            return JsonResponse({
                'rating': evaluation.rating,
                'comment': evaluation.comment
            })
        except Shipment.DoesNotExist:
            return JsonResponse({'error': 'Shipment not found.'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid rating value.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def stickShipment_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            ticked_nos = data.get('tickedNos', [])
            unticked_nos = data.get('untickedNos', [])

            current_ticked_set = set(request.session.get("shipmentTickedNos", []))

            if action == 'select_all':
                # Parse the query params from the payload to apply filters
                query_string = data.get('currentQueryParams', '')
                if query_string.startswith('?'):
                    query_string = query_string[1:]

                # === FIXED: Create MUTABLE QueryDict ===
                query_dict = QueryDict(mutable=True)
                if query_string:
                    # Parse the query string and populate the mutable QueryDict
                    parsed_params = parse_qs(query_string)
                    for key, values in parsed_params.items():
                        query_dict.setlist(key, values)

                # Get the base queryset based on user (mirroring filter_shipment logic)
                if request.user.isCpn:
                    print("User is company, filtering shipments by company.")
                    shipments = Shipment.objects.filter(company=request.user.companyName).order_by("-number")
                elif request.user.isSpl:  # Check if the user is a supplier
                    print("User is supplier, filtering shipments by supplier.")
                    shipments = Shipment.objects.filter(supplier=request.user.supplierName).order_by("-number")
                else:
                    # User is staff/superuser: get ALL shipments
                    print("User is staff/superuser, accessing all shipments.")
                    shipments = Shipment.objects.all().order_by("-number")
                
                # === Handle flag_status manually (copy the workaround)
                removed_flag_vals = None
                if 'flag_status' in query_dict:
                    removed_flag_vals = query_dict.getlist('flag_status')
                    query_dict.pop('flag_status')  # Safe on mutable QueryDict

                # Apply the filters using the parsed query_dict
                filter_form = ShipmentFilter(query_dict, queryset=shipments)
                filtered_queryset = filter_form.qs

                # Manually apply flag_status using the extracted function
                if removed_flag_vals:
                    filtered_queryset = apply_flag_status_filter(filtered_queryset, removed_flag_vals)

                # Apply server-side sorting (mirror filter_shipment logic)
                sort_key = query_dict.get('sort')
                order = query_dict.get('order', 'asc')
                allowed_sort_fields = [
                    'number', 'shipment_id', 'company', 'vessel', 'supplier', 'division', 
                    'quanty', 'c_packing', 'weight', 'unit', 'size', 'docs', 'in_date', 
                    'warehouse', 'by', 'IMP_BL', 'port', 'out_date', 'remark', 'EXP_BL', 
                    'flag_status', 'insert_org', 'correct_org', 'Order_No'
                ]
                if sort_key and sort_key in allowed_sort_fields:
                    prefix = '-' if order == 'desc' else ''
                    filtered_queryset = filtered_queryset.order_by(f'{prefix}{sort_key}')
                else:
                    # Default sort
                    filtered_queryset = filtered_queryset.order_by('-in_date', '-number')

                # Get the 'number' values from the filtered queryset
                ticked_nos = list(filtered_queryset.values_list('number', flat=True))
                current_ticked_set = set(ticked_nos)
                logger.info(f"stickShipment_ajax: Select All action: {len(current_ticked_set)} shipments selected.")

            elif action == 'clear':
                # Clear all selections
                current_ticked_set = set()
                logger.info("stickShipment_ajax: Clear All action.")

            elif action == 'update':
                # Handle individual or page-level updates
                logger.debug(f"stickShipment_ajax: Received tickedNos={ticked_nos}, untickedNos={unticked_nos}")
                for num in ticked_nos:
                    current_ticked_set.add(int(num))
                for num in unticked_nos:
                    current_ticked_set.discard(int(num))

            # Save the updated set back to the session
            request.session["shipmentTickedNos"] = list(current_ticked_set)
            request.session.modified = True

            logger.info(f"stickShipment_ajax: Final shipmentTickedNos count={len(current_ticked_set)}")
            return JsonResponse({
                'status': 'success',
                'total_count': len(current_ticked_set),
                'tickedNos': list(current_ticked_set)
            })
        except json.JSONDecodeError:
            logger.error("stickShipment_ajax: Invalid JSON format")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"stickShipment_ajax: Error: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'Server Error: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid or unhandled request payload.'}, status=400)

@login_required
def approve_pending_shipment(request, pk):
    if not (request.user.isOpr or request.user.is_superuser):
        messages.error(request, "You do not have permission to approve shipments.")
        return redirect('mainPage1')

    pending = get_object_or_404(PendingShipment, pk=pk)
    shipment = Shipment(
        company=pending.company,
        vessel=pending.vessel,
        supplier=pending.supplier,
        quanty=pending.quanty,
        weight=pending.weight,
        size=pending.size,
        flag_status='BLANK',  # Default status
        c_packing='',  # Set empty string as default
        insert_org=pending.submitted_by.userID,
        correct_org=request.user.userID,
        # Add other defaults as needed (e.g., in_date=now(), etc.)
    )
    shipment.save()
    pending.delete()
    messages.success(request, "Shipment approved and added to database.")
    ref = request.META.get('HTTP_REFERER')
    return redirect(ref) if ref else redirect('mainPage1')

@login_required
def reject_pending_shipment(request, pk):
    if not (request.user.isOpr or request.user.is_superuser):
        messages.error(request, "You do not have permission to reject shipments.")
        return redirect('mainPage1')

    pending = get_object_or_404(PendingShipment, pk=pk)
    pending.delete()
    messages.success(request, "Shipment rejected and deleted.")
    ref = request.META.get('HTTP_REFERER')
    return redirect(ref) if ref else redirect('mainPage1')
    
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt  # Optional if JS sends CSRF; test without it
def get_shipment_details_ajax(request):
    """Retrieves shipment details and associated files for modification."""
    if request.method == 'GET' and 'shipment_id' in request.GET:
        try:
            shipment_pk = request.GET.get('shipment_id')
            shipment = get_object_or_404(Shipment, number=shipment_pk)

            # 1. Prepare shipment data (non-file fields) - Complete list for JS
            shipment_data = {
                'number': shipment.number,
                'shipment_id': shipment.shipment_id,
                'company': shipment.company or '',
                'vessel': shipment.vessel or '',
                'supplier': shipment.supplier or '',
                'IMP_BL': shipment.IMP_BL or '',
                'EXP_BL': shipment.EXP_BL or '',
                'Order_No': shipment.Order_No or '',
                'division': shipment.division or '',
                'quanty': shipment.quanty or '',
                'weight': shipment.weight or '',
                'c_packing': shipment.c_packing or '',
                'unit': shipment.unit or '',
                'size': shipment.size or '',
                'docs': shipment.docs or '',
                'in_date': shipment.in_date.isoformat() if shipment.in_date else '',
                'warehouse': shipment.warehouse or '',
                'by': shipment.by or '',
                'port': shipment.port or '',
                'out_date': shipment.out_date.isoformat() if shipment.out_date else '',
                'remark': shipment.remark or '',
            }

            # 2. Prepare file data
            file_list = []
            for file_obj in shipment.files.all():
                file_list.append({
                    'id': file_obj.pk,
                    'file': file_obj.file.url,
                    'file_type': file_obj.file_type,
                    'file_name': file_obj.file.name.split('/')[-1],
                })

            # 3. Combine and return
            response_data = {
                'status': 'success',
                'shipment': shipment_data,
                'files': file_list,
            }
            logger.debug(f"Fetched shipment {shipment_pk} with {len(file_list)} files.")
            return JsonResponse(response_data)

        except Shipment.DoesNotExist:
            logger.error(f"Shipment with pk {shipment_pk} not found.")
            return JsonResponse({'status': 'error', 'message': 'Shipment not found.'}, status=404)
        except Exception as e:
            logger.error(f"Error fetching shipment details: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)