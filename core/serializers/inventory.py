from rest_framework import serializers
from ..models.inventory import Inventory
from .part import PartSerializer,PartTypeSerializer
from .aircraft import AircraftSerializer

class InventorySerializer(serializers.ModelSerializer):
    """
    Envanter görüntüleme için serializer.
    İlişkili alanları nested olarak gösterir.
    """
    part_type = PartTypeSerializer(read_only=True)
    aircraft_type = AircraftSerializer(read_only=True)
    updated_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 
            'part_type', 
            'aircraft_type', 
            'quantity', 
            'minimum_quantity',
            'updated_at'
        ]
    def get_part_type(self, obj) -> dict:
        return {
            'id': obj.part_type.id,
            'name': obj.part_type.name
        }
    
    def get_aircraft_type(self, obj) -> dict:
        return {
            'id': obj.aircraft_type.id,
            'name': obj.aircraft_type.name
        }
    
    def get_status(self, obj) -> str:
        """
        Stok durumunu kontrol edip uygun durum mesajını döndürür.        
        Returns:
            str: "Stok Yok", "Kritik Seviye" veya "Yeterli"
        """
        if obj.quantity <= 0:
            return "Stok Yok"
        elif obj.quantity < obj.minimum_quantity:
            return "Kritik Seviye"
        return "Yeterli"

class InventoryPatchSerializer(serializers.ModelSerializer):
    """
    Envanter güncelleme için serializer.
    sadece minimum_quantity alanını içerir
    """
    minimum_quantity = serializers.IntegerField(required=True, min_value=0)
    class Meta:
        model = Inventory
        fields = ['minimum_quantity']







