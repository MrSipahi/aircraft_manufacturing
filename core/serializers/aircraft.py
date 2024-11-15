from rest_framework import serializers
from ..models.aircraft import  Aircraft

class AircraftSerializer(serializers.ModelSerializer):
   """Hava aracı için serializer"""
   class Meta:
       model = Aircraft
       fields = ['id', 'name']


from rest_framework import serializers
from ..models.aircraft import Aircraft, AircraftRequirement
from ..models.part import Part

class AircraftRequirementSerializer(serializers.ModelSerializer):
    """Hava aracı için gerekli parça serializer"""
    part_type = serializers.SerializerMethodField()

    class Meta:
        model = AircraftRequirement
        fields = ['id', 'aircraft_type', 'part_type', 'quantity']

    def get_part_type(self, obj) -> dict:
        return {
            'id': obj.part_type.id,
            'name': obj.part_type.name
        }

class AvailablePartSerializer(serializers.ModelSerializer):
    """Kullanılabilir parça serializer"""
    type = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = ['id', 'name', 'type']

    def get_type(self, obj) -> dict:
        return {
            'id': obj.type.id,
            'name': obj.type.name
        }