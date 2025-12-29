from django import forms
from django.forms import TextInput, DateInput, Textarea
from django.forms import CharField, DateField, ChoiceField
from django.forms import ValidationError
from datetime import date, datetime

from User.models import *
from User.form_validators import *
from Shipment.models import *


#=================================================================================#
#========== Validator fields for the form ========================================#
date_format = '%Y%m%d'
date_format_error = {
    'invalid': "Wrong date format. Must be YYYYMMDD",
}
date_format_errorM = {
    'invalid': "Must be YYYYMMDD",
}

#=================================================================================#
def date_form_validator(
    date_string: str,
) -> str:
    if date_string == "" or date_string is None:
        return ""
    else:
        try:
            datecheck = bool(datetime.strptime(date_string, date_format))
        except ValueError:
            datecheck = False

        if datecheck:
            return date_string
        else:
            raise forms.ValidationError("Wrong date format! (YYYYMMDD)")
#=================================================================================#

#=================================================================================#
def company_empty_validator(
    company: str,
) -> str:
    if not company:
        raise forms.ValidationError("Company field can not be empty!")

    return company
#=================================================================================#


#=================================================================================#
#========== Form To Register New Order ===========================================#
class ShipmentRegistrationForm(forms.ModelForm):
    shipment_id = forms.CharField(label="Shipment ID", required=False, disabled=True)

    in_date = DateField(label="IN", required=False,
                        widget=forms.DateInput(format=date_format),
                        initial=date.today(), input_formats=[date_format],
                        error_messages=date_format_error)
    out_date = DateField(label="OUT", required=False,
                         widget=forms.DateInput(format=date_format),
                         initial=date.today(), input_formats=[date_format],
                         error_messages=date_format_error)
    division = ChoiceField(label="DIVISIONS", required=False,
                           initial="D", choices=DIVISION_CHOICES0)
    
    c_packing = ChoiceField(
        label="C.PACKING",
        required=False,              # CRITICAL: Allow an empty value
        choices=CPACKING_CHOICES0
    )
    company = CharField(label="COMPANY", required=True,
                          initial="", validators=[company_empty_validator])
    vessel = CharField(label="VESSEL", required=True)


    class Meta:
        model = Shipment
        fields = ('shipment_id','company', 'vessel', 'docs', 'Order_No', 'supplier', 'quanty', 'unit',
                  'size', 'weight', 'in_date', 'warehouse', 'by', 'IMP_BL',
                  'port', 'out_date', 'remark', 'EXP_BL', 'c_packing',
                  'image', 'image1', 'image2', 'pdf_file', 'division')

    # Note: MUST HAVE THESE VALIDATORS!!!
    def clean_company(self):
        return company_empty_validator(self.cleaned_data.get('company'))
    def clean_vessel(self):
        return company_empty_validator(self.cleaned_data.get('vessel'))
#=================================================================================#


#========== Form To Modify Orders ================================================#
class ShipmentModificationForm(forms.ModelForm):
    shipment_id = forms.CharField(label="Shipment ID", required=False, disabled=True)
    in_dateM = DateField(label="Date In", required=False,
                         widget=forms.DateInput(format=date_format),
                         initial=date.today(), input_formats=[date_format],
                         error_messages=date_format_errorM)
    out_dateM = DateField(label="Date Out", required=False,
                          widget=forms.DateInput(format=date_format),
                          initial=date.today(), input_formats=[date_format],
                          error_messages=date_format_errorM)
    companyM = CharField(label="COMPANY", required=False,
                           initial="")
    vesselM = CharField(label="VESSEL", required=False, max_length=LG)
    supplierM = CharField(label="SUPPLIER", required=False, max_length=XL)
    warehouseM = CharField(label="WAREHOUSE", required=False, max_length=LG)
    divisionM = ChoiceField(label="DIVISION", required=False,
                            initial="D", choices=DIVISION_CHOICES0)
    flag_statusM = ChoiceField(label="STATE", required=False,
                               initial="", choices=FLAG_CHOICES0)
    EXP_BLM = CharField(label="EXP.BL", required=False)
    portM = CharField(label="PORT", required=False)
    remarkM = CharField(label="REMARK", required=False)
    docsM = CharField(label="DOC", required=False)
    Order_NoM = CharField(label="Order.No", required=False)
    quantyM = CharField(label="QTY", required=False)
    unitM = CharField(label="UNIT", required=False)
    sizeM = CharField(label="SIZE", required=False)
    weightM = CharField(label="WEIGHT", required=False)
    IMP_BLM = CharField(label="IM.BL", required=False)

    class Meta:
        model = Shipment
        fields = ('shipment_id','companyM', 'vesselM', 'supplierM', 'warehouseM', 'divisionM',
                  'flag_statusM', 'in_dateM', 'out_dateM', 'EXP_BLM', 'portM', 'remarkM')
