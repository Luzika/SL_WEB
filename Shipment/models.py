from django.db import models
from django.utils.timezone import now
from django.core.files import File

from User.models import *
from Shipment.override_existing import OverrideExisting
import datetime
import django_filters
from django_filters import ChoiceFilter, CharFilter
from django_filters import DateFromToRangeFilter
from django_filters.widgets import RangeWidget

from django.db import transaction
import random
import string
import requests
from django.utils import timezone

# Add to constants at the top
SM = 50
MD = 100
LG = 200
XL = 1000

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
# Create your models here.
IMAGE_PATH = "imageShipment/"
PDF_PATH = "pdfShipment/"
BARCODE_PATH = "barcodeShipment/"

PRELIST_DATA = {
  # "company": [
  #     "GOLTENS",
  #     "MAN",
  #     "JW",
  #     "CMSHIP",
  #     "MARUBISHI",
  #     "STX",
  #     "SUNRIO",
  #     "KNK",
  #     "EUCO",
  #     "SHI OCEAN",
  #     "GLOVIS",
  #     "KSS",
  #     "GOWIN",
  #     "INTERGIS",
  #     "SUNAMI",
  #     "INTERGIS",
  #     "SUNAMI",
  #     "보성상사",
  #     "이강공사",
  #     "오션마린",
  #     "CENTRA",
  #     "POSSM",
  #     "DORVAL",
  #     "SAEHAN",
  #     "FORTUNE WILL",
  #     "SEOYANG",
  #     "KLCSM",
  #     "DAN MO",
  # ],
  "warehouse": [
      "SL",
      "KIM-IGS",
      "ICN-IGS",
      "ICN-CSW",
      "PUS-CSW",
      "SHA",
      "OSA",
      "RTM",
  ],
  "by": [
      "DHL",
      "FDX",
      "TNT",
      "AIR",
      "SEA",
      "SFX",
  ],
  "division": [
      "D",
      "B",
      "L",
  ],
  "flag": [
      "BLANK",
      "STAY",
      "START",
      "COMPLETED",
  ],
  "unit": [
      "CT",
      "PL",
      "WC",
      "PKG",
  ],
  "cpacking": [
      "YES",
      "NO",
  ],
}

# COMPANY_LIST = PRELIST_DATA["company"]
COMPANY_LIST = []
WAREHOUSE_LIST = PRELIST_DATA["warehouse"]
BY_LIST = PRELIST_DATA["by"]
DIVISION_LIST = PRELIST_DATA["division"]
FLAG_LIST = PRELIST_DATA["flag"]
UNIT_LIST = PRELIST_DATA["unit"]
CPACKING_LIST = PRELIST_DATA["cpacking"]
COMPANY_CHOICES0 = [(c,c) for c in COMPANY_LIST]
FLAG_CHOICES0 = [(c,c) for c in FLAG_LIST]
DIVISION_CHOICES0 = [(c,c) for c in DIVISION_LIST]
CPACKING_CHOICES0 = [(c,c) for c in CPACKING_LIST]


#=================================================================================#
#========== Functions to define the path of uploaded files =======================#
def image_path(instance, filename):
  return IMAGE_PATH + '/{0}_{1}_{2}/{3}'.format(
    instance.company.replace(" ", "."),
    instance.vessel.replace(" ", "."),
    instance.in_date,
    filename
  )

def pdf_path(instance, filename):
  return PDF_PATH + '/{0}_{1}_{2}/{3}'.format(
    instance.company.replace(" ", "."),
    instance.vessel.replace(" ", "."),
    instance.in_date,
    filename
  )

def barcode_path(instance, filename):
  return BARCODE_PATH + '/{0}_{1}_{2}/{3}'.format(
    instance.company.replace(" ", "."),
    instance.vessel.replace(" ", "."),
    instance.in_date,
    filename
  )
#=================================================================================#


#=================================================================================#
#========== Main model for Shipment ==============================================#
class Shipment(models.Model):
  number = models.BigAutoField(db_column="no", primary_key=True)

  shipment_id = models.CharField(max_length=SM, unique=False, blank=True, null=True, db_index=True)

  barcode = models.ImageField(db_column="barcode", blank=True,
                              upload_to=barcode_path,
                              storage=OverrideExisting())
  colorpick = models.CharField(db_column="color_status", blank=True,
                               max_length=SM)
  colordiv = models.CharField(db_column="color_div", blank=True,
                              max_length=SM, default="black")
  kantor_id = models.CharField(db_column="kantor_id", blank=True,
                               max_length=MD)
  insert_org = models.CharField(db_column="insert_org", blank=True,
                                max_length=MD)
  correct_org = models.CharField(db_column="correct_org", blank=True,
                                 max_length=MD)
  reg_date = models.DateTimeField(db_column="regdate", auto_now=True)
  company = models.CharField(db_column="company", blank=True,
                             max_length=LG)
  vessel = models.CharField(db_column="vessel", blank=True,
                            max_length=LG)
  by = models.CharField(db_column="by1", blank=True,
                        max_length=MD)
  IMP_BL = models.CharField(db_column="imp_bl", blank=True,
                          max_length=LG)
  # ASKno has been removed.
  docs = models.TextField(db_column="doc", blank=True,
                          max_length=XL)
  Order_No = models.TextField(db_column="order_no", blank=True,
                          max_length=XL)
  c_packing = models.CharField(db_column="c_packing",
                               max_length=SM,
                               choices=CPACKING_CHOICES0,
                               null=True, blank=True)
  supplier = models.TextField(db_column="supplier", blank=True,
                              max_length=XL)
  quanty = models.CharField(db_column="qty", blank=True,
                            max_length=SM)
  unit = models.CharField(db_column="unit", blank=True,
                          max_length=SM)
  size = models.TextField(db_column="size", blank=True,
                          max_length=XL)
  weight = models.CharField(db_column="weight", blank=True,
                            max_length=LG)
  in_date = models.DateField(db_column="in1", blank=True, null=True,
                             max_length=SM, default=now)
  warehouse = models.CharField(db_column="whouse", blank=True, null=True,
                               max_length=LG)
  warehouse2 = models.CharField(db_column="whouse2", blank=True, null=True,
                                max_length=LG)
  last_whouse = models.CharField(db_column="last_whouse", blank=True,
                                 max_length=LG)
  wh_timestamp = models.DateTimeField(db_column="wh_timestamp1",
                                      max_length=MD,
                                      blank=True, null=True)
  wh_timestamp2 = models.DateTimeField(db_column="wh_timestamp2",
                                       max_length=MD,
                                       blank=True, null=True)
  port = models.CharField(db_column="port", blank=True,
                          max_length=LG)
  out_date = models.DateField(db_column="out1", blank=True, null=True,
                              max_length=SM)
  remark = models.TextField(db_column="remark", blank=True,
                            max_length=XL)
  # memo has been removed.
  image = models.ImageField(db_column="img", blank=True, null=True, default="",
                            max_length=XL,
                            upload_to=image_path,
                            storage=OverrideExisting())
  image1 = models.ImageField(db_column="img1", blank=True, null=True, default="",
                             max_length=XL,
                             upload_to=image_path,
                             storage=OverrideExisting())
  image2 = models.ImageField(db_column="img2", blank=True, null=True, default="",
                             max_length=XL,
                             upload_to=image_path,
                             storage=OverrideExisting())
  pdf_file = models.FileField(db_column="pdf", blank=True, null=True, default="",
                              max_length=XL,
                              upload_to=pdf_path,
                              storage=OverrideExisting())
  division = models.CharField(db_column="division", blank=True,
                              max_length=SM, choices=DIVISION_CHOICES0)
  flag_status = models.CharField(db_column="flg", blank=True,
                                 max_length=SM, choices=FLAG_CHOICES0)
  EXP_BL = models.CharField(db_column="exp_bl", blank=True,
                                max_length=LG)
  work = models.CharField(db_column="work", blank=True,
                          max_length=SM)
  work_regdate = models.DateTimeField(db_column="work_regdate",
                                      max_length=MD,
                                      blank=True, null=True)
  location = models.CharField(max_length=255, blank=True, null=True)

  def __str__(self): # type: ignore
    return self.number

  def save(self, *args, **kwargs):
    if not self.shipment_id and self.company and self.vessel and self.in_date:
        with transaction.atomic():
            # Generate shipment_id and ensure uniquenesskocat
            while True:
                shipment_id = generate_shipment_id(self.company, self.vessel, self.in_date)
                if not Shipment.objects.filter(shipment_id=shipment_id).exists():
                    self.shipment_id = shipment_id
                    break
    # Existing save logic
    if self.pk:
        old_shipment = Shipment.objects.get(pk=self.pk)
        user = kwargs.pop('user', None)
        changed_fields = []

        if old_shipment.warehouse != self.warehouse:
            changed_fields.append(('warehouse', old_shipment.warehouse, self.warehouse))
        if old_shipment.flag_status != self.flag_status:
            changed_fields.append(('flag_status', old_shipment.flag_status, self.flag_status))
        if old_shipment.in_date != self.in_date:
            changed_fields.append(('in_date', old_shipment.in_date, self.in_date))
        if old_shipment.out_date != self.out_date:
            changed_fields.append(('out_date', old_shipment.out_date, self.out_date))

        # for field, old_value, new_value in changed_fields:
        #     movement_type = {
        #         'warehouse': 'WAREHOUSE',
        #         'flag_status': 'STATUS',
        #         'in_date': 'DATE',
        #         'out_date': 'DATE',
        #     }.get(field, 'OTHER')

        #     # Define location based on flag_status
        #     location = self.location
        #     if field == 'flag_status':
        #         if self.flag_status == 'START':
        #             location = f"Origin: {self.warehouse or 'Unknown'}"
        #         elif self.flag_status == 'STAY':
        #             location = f"In Transit: {self.warehouse or 'Unknown'}"
        #         elif self.flag_status == 'COMPLETED':
        #             location = f"Destination: {self.warehouse or 'Unknown'}"
        #         elif self.flag_status == 'BLANK':
        #             location = 'Not Assigned'

        #     ShipmentMovement.objects.create(
        #         shipment=self,
        #         warehouse=self.warehouse if field == 'warehouse' else old_shipment.warehouse,
        #         flag_status=self.flag_status if field == 'flag_status' else old_shipment.flag_status,
        #         in_date=self.in_date if field == 'in_date' else old_shipment.in_date,
        #         out_date=self.out_date if field == 'out_date' else old_shipment.out_date,
        #         changed_by=user.userID if user and hasattr(user, 'userID') else 'Unknown',
        #         movement_type=movement_type,
        #         location=location,
        #         remark=f"Changed {field} from {old_value} to {new_value}"
        #     )
        
        #####################################################################################
        # New: Detect key events and send to VMS
        # vms_url = "https://vms-system.com/api/update-shipment/"  # VMS provides this URL
        # vms_token = "your-vms-secret-token"  # VMS provides this (put in settings.py for security)

        # send_to_vms = False
        # payload = {
        #     "shipment_id": self.shipment_id,
        #     "warehouse": self.warehouse,
        #     "remark": self.remark,
        #     "timestamp": timezone.now().isoformat(),
        # }

        # if old_shipment.flag_status != self.flag_status:
        #     if self.flag_status == 'STAY':  # Received in warehouse
        #         payload["event"] = "received_in_warehouse"
        #         send_to_vms = True
        #     elif self.flag_status == 'COMPLETED':  # Shipped to vessel
        #         payload["event"] = "shipped_to_vessel"
        #         payload["out_date"] = self.out_date.isoformat() if self.out_date else None
        #         send_to_vms = True

        # if send_to_vms:
        #     try:
        #         headers = {
        #             "Authorization": f"Token {vms_token}",
        #             "Content-Type": "application/json"
        #         }
        #         response = requests.post(vms_url, json=payload, headers=headers)
        #         if response.status_code != 200:
        #             print(f"VMS send failed: {response.text}")  # Log error (use logging in production)
        #     except Exception as e:
        #         print(f"Error sending to VMS: {e}")  # Log (replace with logging)
        #####################################################################################

    super().save(*args, **kwargs)

  class Meta:
    db_table = "pla_databoard"

#=================================================================================#
#============================ShipmentMovement================================#
class ShipmentMovement(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='movements')
    timestamp = models.DateTimeField(auto_now_add=True)
    warehouse = models.CharField(max_length=LG, blank=True, null=True, choices=[(w, w) for w in WAREHOUSE_LIST])
    flag_status = models.CharField(max_length=SM, blank=True, choices=FLAG_CHOICES0)
    in_date = models.DateField(blank=True, null=True)
    out_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=LG, blank=True, null=True)  # New field for specific location
    changed_by = models.CharField(max_length=MD, blank=True)
    remark = models.TextField(max_length=XL, null=True, blank=True)
    movement_type = models.CharField(max_length=SM, blank=True, choices=[
        ('STATUS', 'Status'),
        ('WAREHOUSE', 'Warehouse'),
        ('LOCATION_UPDATE', 'Location Update'),
        ('DATE', 'Date'),
        ('OTHER', 'Other'),
    ])
    flag_statrus = models.CharField(max_length=SM, blank=True, choices=[
        ('START', 'Start'),
        ('STAY', 'Stay'),
        ('COMPLETED', 'Completed'),
        ('BLANK', 'Blank'),
    ], default='BLANK')
    transport_mode = models.CharField(max_length=MD, choices=[
        ('VESSEL', 'Vessel'),
        ('AIRPLANE', 'Airplane'),
        ('TRUCK', 'Truck'),
        ('PORT', 'Port'),
        ('TRAIN', 'Train'),
        ('OTHER', 'Other'),
    ], null=True, blank=True)
    def __str__(self):
        return f"{self.shipment.shipment_id} - {self.movement_type} at {self.timestamp}"

    class Meta:
        db_table = "pla_shipment_movement"
        ordering = ['-timestamp']

#=================================================================================#
#========== Main model for Shipment Filter (django-filters) ======================#
class ShipmentFilter(django_filters.FilterSet):
  company = CharFilter(label="Company", lookup_expr="icontains")
  supplier = CharFilter(label="Supplier", lookup_expr="icontains")
  vessel = CharFilter(label="Vessel", lookup_expr="icontains")
  Order_No = CharFilter(label="Order No", lookup_expr="icontains")
  quanty = CharFilter(label="QUANTY", lookup_expr="icontains")
  weight = CharFilter(label="WEIGHT", lookup_expr="icontains")
  port = CharFilter(label="PORT", lookup_expr="icontains")
  EXP_BL = CharFilter(label="EXP BL", lookup_expr="icontains")
  warehouse = CharFilter(label="Warehouse", lookup_expr="icontains")
  shipment_id = CharFilter(label="Shipment ID", lookup_expr="icontains")
  division = ChoiceFilter(label="Division", choices=DIVISION_CHOICES0)
  # flag_status = ChoiceFilter(label="State", choices=FLAG_CHOICES0)
  # CHANGE: Use MultipleChoiceFilter instead of ChoiceFilter
  flag_status = django_filters.MultipleChoiceFilter(
      choices=FLAG_CHOICES0,
      lookup_expr='in'  # This tells the database to search for "status IN (value1, value2)"
  )
  in_date_range = django_filters.DateFromToRangeFilter(
    field_name='in_date', widget=RangeWidget(attrs={'placeholder': 'YYYYMMDD'}))
  out_date_range = django_filters.DateFromToRangeFilter(
    field_name='out_date', widget=RangeWidget(attrs={'placeholder': 'YYYYMMDD'}))


  class Meta:
    model = Shipment
    fields = ['in_date_range', 'out_date_range', 'company', 'supplier', 'vessel',
              'Order_No', 'quanty', 'weight', 'port', 'EXP_BL', 'warehouse',
              'division', 'flag_status', 'shipment_id']

  def __init__(self, *args, **kwargs):
    super(ShipmentFilter, self).__init__(*args, **kwargs)
    self.form.fields['in_date_range'].fields[0].input_formats = ['%Y%m%d'] # type: ignore
    self.form.fields['in_date_range'].fields[1].input_formats = ['%Y%m%d'] # type: ignore
    self.form.fields['out_date_range'].fields[0].input_formats = ['%Y%m%d'] # type: ignore
    self.form.fields['out_date_range'].fields[1].input_formats = ['%Y%m%d'] # type: ignore
#=================================================================================#

class ShipmentEvaluation(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='evaluations')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # type: ignore
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['shipment']  # One evaluation per shipment

    def __str__(self):
        return f"{self.rating} stars for {self.shipment.shipment_id}"

#=========================== Model for multi pdf and images ==============================#
class ShipmentFile(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='shipment_files/')
    file_type = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('image', 'Image')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

#=========================== Model customer adding ==============================#
class PendingShipment(models.Model):
    company = models.CharField(max_length=LG, blank=True)
    vessel = models.CharField(max_length=LG, blank=True)
    supplier = models.TextField(max_length=XL, blank=True)
    quanty = models.CharField(max_length=SM, blank=True)  # Quantity
    weight = models.CharField(max_length=LG, blank=True)
    size = models.TextField(max_length=LG, blank=True)
    submitted_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='pending_shipments')
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sl_pending_shipments"
        ordering = ['-submission_date']

    def __str__(self):
        return f"Pending {self.company} - {self.vessel} by {self.submitted_by.userID}"
