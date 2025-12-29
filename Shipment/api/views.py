from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from Shipment.models import Shipment, ShipmentMovement
from .serializers import ExternalUpdateSerializer

class ExternalShipmentAPI(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_source(self, request):
        username = request.user.userID.lower() if hasattr(request.user, 'userID') else request.user.username.lower()
        if 'vms' in username:
            return 'vms'
        if 'man' in username:
            return 'manufacturer'
        return None

    @action(detail=False, methods=['patch'], url_path='update/(?P<shipment_id>[^/.]+)')
    def update_shipment(self, request, shipment_id):
        source = self.get_source(request)
        if not source:
            return Response({"detail": "Unauthorized source."}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Use shipment_id field (not id/pk) — matches your model
            shipment = Shipment.objects.get(shipment_id=shipment_id)
        except Shipment.DoesNotExist:
            return Response({"detail": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExternalUpdateSerializer(
            shipment,
            data=request.data,
            partial=True,
            context={'source': source}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail": "Shipment updated successfully.",
                "shipment_id": shipment_id,
                "updated_by": source
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Optional: Allow external systems to read shipment status
    @action(detail=False, methods=['get'], url_path='detail/(?P<shipment_id>[^/.]+)')
    def get_detail(self, request, shipment_id):
        try:
            shipment = Shipment.objects.filter(shipment_id=shipment_id).values(
                'shipment_id', 'company', 'vessel', 'supplier', 'quanty', 'unit',
                'warehouse', 'flag_status', 'by', 'in_date', 'out_date',
                'remark', 'division', 'IMP_BL', 'port'
            ).first()

            if shipment:
                return Response(shipment)
            else:
                return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)