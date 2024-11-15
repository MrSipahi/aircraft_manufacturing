from rest_framework import serializers
from ..models.aircraft import Aircraft
from ..models.assembly import Assembly
from ..models.part import Part
from .aircraft import AircraftSerializer
from .part import PartSerializer

class AssemblyCreateSerializer(serializers.ModelSerializer):
    # Montaj için gerekli parçaları validasyon için kullanmak için
    parts = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Part.objects.select_related(
            'type', 
            'aircraft_type'
        ).filter(is_used=False)
    )

    class Meta:
        model = Assembly
        fields = ['aircraft_type', 'parts', 'notes']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user:
            return serializers.ValidationError("Kullanıcı bilgisi bulunamadı.")
        
        
        if not request.user.team:
            raise PermissionError("Kullanıcının takımı bulunamadı!")

        # Montaj takımı kontrolü
        if not request.user.can_assemble: 
            raise PermissionError("Sadece montaj takımı montaj yapabilir.")


        # Aircraft için gerekli parçaları kontrol et
        aircraft = data['aircraft_type']
        requirements = aircraft.requirements.all()
        
        required_parts = {}
        for req in requirements:
            required_parts[req.part_type_id] = req.quantity

        # Seçilen parçaları kontrol et
        selected_parts = {}
        # Parçaların varlığını ve kullanılabilirliğini toplu kontrol et
        part_ids = [part.id for part in data['parts']]
        existing_parts = Part.objects.filter(
            id__in=part_ids, 
            is_used=False
        ).select_related('type', 'aircraft_type')
        
        if len(existing_parts) != len(part_ids):
            raise serializers.ValidationError("Bazı parçalar bulunamadı veya daha önce kullanılmış!")

        for part in existing_parts:
            if part.is_used:
                raise serializers.ValidationError(f"{part} daha önce kullanılmış!")
            if part.aircraft_type != aircraft:
                raise serializers.ValidationError(f"{part} bu uçak tipi için uygun değil!")
            
            part_type_id = part.type_id
            selected_parts[part_type_id] = selected_parts.get(part_type_id, 0) + 1

        # Gerekli parça sayılarını kontrol et
        for part_type_id, required_quantity in required_parts.items():
            selected_quantity = selected_parts.get(part_type_id, 0)
            if selected_quantity != required_quantity:
                raise serializers.ValidationError(
                    f"Bu parça tipi için {required_quantity} adet gerekli, "
                    f"{selected_quantity} adet seçilmiş."
                )

        return data

class AssemblySerializer(serializers.ModelSerializer):
    aircraft_type = AircraftSerializer(read_only=True)
    parts = PartSerializer(many=True, read_only=True)
    assembled_by = serializers.StringRelatedField(read_only=True)
    assembled_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Assembly
        fields = [
            'id',
            'aircraft_type',
            'parts',
            'assembled_by',
            'assembled_at',
            'notes',
            'is_complete'
        ]

    def get_aircraft_type(self, obj) -> dict:
        return {
            'id': obj.aircraft_type.id,
            'name': obj.aircraft_type.name
        }

    def get_assembled_by(self, obj) -> str:
        team_info = str(obj.assembled_by.team) if obj.assembled_by.team else "Takım Atanmamış"
        return f"{obj.assembled_by.get_full_name()} - {team_info}"

    def get_parts(self, obj) -> dict:
        return PartSerializer(obj.parts.all(), many=True).data