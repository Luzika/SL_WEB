from rest_framework import serializers
from Shipment.models import Shipment, ShipmentMovement

# Define exactly what each external system is allowed to update
ALLOWED_FIELDS = {
    'vms': [
        'company', 'vessel', 'supplier', 'Order_No', 'quanty', 'unit',
        'size', 'weight', 'in_date', 'c_packing', 'docs', 'remark', 'division'
    ],
    'manufacturer': [
        'by', 'IMP_BL', 'out_date', 'port', 'warehouse', 'remark'
    ],
}

class ExternalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'

    def validate(self, attrs):  # ← ĐỔI TỪ "data" THÀNH "attrs"
        source = self.context.get('source')
        if source not in ALLOWED_FIELDS:
            raise serializers.ValidationError("Invalid source system.")

        allowed = ALLOWED_FIELDS[source]
        invalid_fields = [field for field in attrs if field not in allowed]  # ← cũng đổi data → attrs
        if invalid_fields:
            raise serializers.ValidationError(
                f"You are not allowed to update: {', '.join(invalid_fields)}"
            )
        return attrs

    def update(self, instance, validated_data):
        source = self.context['source']

        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Auto set flag_status based on source
        if source == 'vms':
            instance.flag_status = 'START'
        elif source == 'manufacturer':
            instance.flag_status = 'STAY'

        instance.save()

        # Log movement
        ShipmentMovement.objects.create(
            shipment=instance,
            movement_type='STATUS' if source == 'vms' else 'WAREHOUSE',
            warehouse=instance.warehouse or '',
            flag_status=instance.flag_status or '',
            remark=f"Updated by {source.upper()} via API",
            changed_by=f"{source.upper()}_API"
        )

        return instance
    
    