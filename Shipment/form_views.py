from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from Shipment.models import *
from Shipment.forms import ShipmentRegistrationForm, ShipmentModificationForm
from datetime import datetime
import copy
from django.db import transaction
import logging as logger
#=================================================================================#
def register_shipment(
    request,
    current_context: dict,
    form_keyword: str="shipmentRegForm",
    form_reload: forms.ModelForm=ShipmentRegistrationForm,
) -> dict:
    result = dict(current_context)
    form_result = form_reload(request.POST, request.FILES)

    # Check if the form is completely empty
    form_data = request.POST.dict()
    form_fields = {k: v.strip() for k, v in form_data.items() if k not in ['csrfmiddlewaretoken', 'addShipment', 'clicked']}
    if not any(form_fields.values()):
        messages.warning(request, "Cannot add a shipment with all fields empty.")
        result[form_keyword] = form_reload()
        return result


    # === ADD THIS DEBUG LOGGING BLOCK ===
    logger.info(f"Form validation check: is_valid = {form_result.is_valid()}")

    if not form_result.is_valid():
        logger.warning("Form validation FAILED. Full errors below:")
        logger.warning(f"Errors (as data): {form_result.errors.as_data()}")
        logger.warning(f"Errors (as text): {form_result.errors.as_text()}")

        # Optional: Log non-field errors (e.g., form-wide issues)
        if form_result.non_field_errors():
            logger.warning(f"Non-field errors: {form_result.non_field_errors()}")

        # Optional: Log cleaned_data to see what passed partial validation
        if hasattr(form_result, 'cleaned_data'):
            logger.debug(f"Cleaned data (partial): {form_result.cleaned_data}")
    else:
        logger.info("Form validation PASSED. Proceeding to save.")

    # Validate the form
    if form_result.is_valid():
        # First, save the main form to create the shipment object
        shipment = form_result.save(commit=False)
        shipment.insert_org = request.user.userID
        shipment.work_regdate = datetime.today().strftime('%Y-%m-%d')

        if shipment.division == "B":
            shipment.colordiv = "red"
        elif shipment.division == "L":
            shipment.colordiv = "blue"
        else:
            shipment.colordiv = "black"

        # Save the shipment object to the database
        shipment.save()

        # === New code to handle multiple files ===
        # Handle multiple PDF files
        for pdf_file in request.FILES.getlist('pdf_file', []):
            ShipmentFile.objects.create(
                shipment=shipment,
                file=pdf_file,
                file_type='pdf'
            )

        # Handle multiple image files
        for image_file in request.FILES.getlist('image_file', []):
            ShipmentFile.objects.create(
                shipment=shipment,
                file=image_file,
                file_type='image'
            )
        # === End of new code ===

        messages.success(request, "Shipment added successfully!")
        form_result = form_reload() # Reset the form after success
    else:
        # If form is not valid, re-render with errors
        form_result = form_reload(request.POST, request.FILES)

    result[form_keyword] = form_result
    return result
#=================================================================================#
def adjust_shipment(
    request,
    current_context: dict,
    form_keyword: str="shipmentRegForm",
    clicked_keyword: str="clicked",
    form_reload: forms.ModelForm=ShipmentRegistrationForm,
) -> dict:
    result = dict(current_context)
    if not request.POST.get(clicked_keyword):
        return result

    try:
        id_clicked = int(request.POST[clicked_keyword])
        shipment_adjusted = Shipment.objects.get(number=id_clicked)
    except (ValueError, Shipment.DoesNotExist):
        result['error'] = "Shipment not found or invalid ID."
        return result

    form_result = form_reload(request.POST)


        # === ADD THIS DEBUG LOGGING BLOCK ===
    logger.info(f"Form validation check: is_valid = {form_result.is_valid()}")

    if not form_result.is_valid():
        logger.warning("Form validation FAILED. Full errors below:")
        logger.warning(f"Errors (as data): {form_result.errors.as_data()}")
        logger.warning(f"Errors (as text): {form_result.errors.as_text()}")

        # Optional: Log non-field errors (e.g., form-wide issues)
        if form_result.non_field_errors():
            logger.warning(f"Non-field errors: {form_result.non_field_errors()}")

        # Optional: Log cleaned_data to see what passed partial validation
        if hasattr(form_result, 'cleaned_data'):
            logger.debug(f"Cleaned data (partial): {form_result.cleaned_data}")
    else:
        logger.info("Form validation PASSED. Proceeding to save.")


    if form_result.is_valid():
        with transaction.atomic():  # Ensure atomicity for deletes + updates + adds
            # === Handle file deletions ===
            files_to_delete = request.POST.get('files_to_delete', '')
            if files_to_delete:
                try:
                    delete_ids = [int(fid.strip()) for fid in files_to_delete.split(',') if fid.strip().isdigit()]
                    if delete_ids:
                        deleted_count = ShipmentFile.objects.filter(
                            id__in=delete_ids,
                            shipment=shipment_adjusted  # Security: Only delete files for this shipment
                        ).delete()[0]  # Returns (count, {})
                        logger.info(f"Deleted {deleted_count} files for shipment {shipment_adjusted.number}")
                except Exception as e:
                    logger.error(f"Error deleting files: {e}")
                    raise  # Will rollback transaction

        # Update the shipment object with form data, excluding files
        shipment_adjusted.company = form_result.cleaned_data.get('company')
        shipment_adjusted.vessel = form_result.cleaned_data.get('vessel')
        shipment_adjusted.supplier = form_result.cleaned_data.get('supplier')
        shipment_adjusted.EXP_BL = form_result.cleaned_data.get('EXP_BL')
        shipment_adjusted.IMP_BL = form_result.cleaned_data.get('IMP_BL')
        shipment_adjusted.Order_No = form_result.cleaned_data.get('Order_No')

        # Cargo Information
        shipment_adjusted.division = form_result.cleaned_data.get('division')
        shipment_adjusted.quanty = form_result.cleaned_data.get('quanty')
        shipment_adjusted.c_packing = form_result.cleaned_data.get('c_packing')
        shipment_adjusted.weight = form_result.cleaned_data.get('weight')
        shipment_adjusted.unit = form_result.cleaned_data.get('unit')
        shipment_adjusted.size = form_result.cleaned_data.get('size')
        shipment_adjusted.docs = form_result.cleaned_data.get('docs')

        # Logistics&Date Information
        shipment_adjusted.in_date = form_result.cleaned_data.get('in_date')
        shipment_adjusted.out_date = form_result.cleaned_data.get('out_date')
        shipment_adjusted.by = form_result.cleaned_data.get('by')
        shipment_adjusted.warehouse = form_result.cleaned_data.get('warehouse')
        shipment_adjusted.port = form_result.cleaned_data.get('port')
        shipment_adjusted.remark = form_result.cleaned_data.get('remark')

        # === Add new files (your existing code) ===
        for pdf_file in request.FILES.getlist('pdf_file', []):
            ShipmentFile.objects.create(
                shipment=shipment_adjusted,
                file=pdf_file,
                file_type='pdf'
            )
        for image_file in request.FILES.getlist('image_file', []):
            ShipmentFile.objects.create(
                shipment=shipment_adjusted,
                file=image_file,
                file_type='image'
            )

        if shipment_adjusted.division == "B":
            shipment_adjusted.colordiv = "red"
        elif shipment_adjusted.division == "L":
            shipment_adjusted.colordiv = "blue"
        else:
            shipment_adjusted.colordiv = "black"

        shipment_adjusted.correct_org = request.user.userID
        shipment_adjusted.save()

        form_result = form_reload()
    else:
        form_result = form_reload(request.POST, request.FILES)

    result[form_keyword] = form_result
    return result