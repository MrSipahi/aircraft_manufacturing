from rest_framework import serializers
from ..models.part import Part, PartType
from .aircraft import AircraftSerializer

class PartTypeSerializer(serializers.ModelSerializer):
   """Parça tipi için serializer"""
   class Meta:
       model = PartType
       fields = ['id', 'name']


class PartSerializer(serializers.ModelSerializer):
    """
    Parça görüntüleme için serializer.
    İlişkili alanları nested olarak gösterir.
    """
    type = PartTypeSerializer(read_only=True)
    aircraft_type = AircraftSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = [
            'id', 
            'name', 
            'type', 
            'aircraft_type', 
            'created_by', 
            'created_at',
            'is_used',
            'status'
        ]
        
    def get_status(self, obj) -> str:
        """
        Parçanın durumunu string olarak döndürür
        Returns:
            str: "Kullanıldı" veya "Stokta"
        """
        return "Kullanıldı" if obj.is_used else "Stokta"
    
    def get_type(self, obj) -> dict:
        return {
            'id': obj.type.id,
            'name': obj.type.name
        }

    def get_aircraft_type(self, obj) -> dict:
        return {
            'id': obj.aircraft_type.id,
            'name': obj.aircraft_type.name
        }

    def get_created_by(self, obj) -> str:
        team_info = str(obj.created_by.team) if obj.created_by.team else "Takım Atanmamış"
        return f"{obj.created_by.get_full_name()} - {team_info}"
   

class PartCreateSerializer(serializers.ModelSerializer):
    """
    Parça oluşturma ve güncelleme için serializer.
    İlişkili alanları ID olarak alır.
    """
    class Meta:
        model = Part
        fields = ['name', 'type', 'aircraft_type']

    def validate(self, data):
        """
        Parça oluşturma/güncelleme validasyonları
        """

        # Kullanıcı bilgisi kontrolü
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Kullanıcı bilgisi bulunamadı.")
        
        # Takım kontrolü
        if not request.user.team:
            raise serializers.ValidationError("Kullanıcının takımı bulunamadı!")
        
        # Montaj takımı kontrolü
        if request.user.team.is_assembly_team:
            raise serializers.ValidationError("Montaj takımı parça üretemez.")
        
        # Parça tipi yetkisi kontrolü
        if not request.user.can_produce_part(data['type']):
            raise serializers.ValidationError(f"Bu tip parça ({data['type'].name}) üretme yetkiniz yok.")
        
        return data

    def create(self, validated_data):
        """
        Parça oluşturma
        created_by alanını otomatik doldurur
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)