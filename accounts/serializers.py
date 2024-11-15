
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team

User = get_user_model()

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'is_assembly_team', 'part_type')

class UserSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    can_assemble = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name',
            'full_name',
            'team',
            'permissions',
            'can_assemble',
            'is_active',
            'is_superuser'
        )

    def get_full_name(self, obj) -> str:
        return obj.get_full_name()

    def get_permissions(self, obj) -> list:
        return list(obj.team.cache_permissions()) if obj.team else []

    def get_can_assemble(self, obj) -> bool:
        return obj.can_assemble()


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    team_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'team_id',
            'is_active',
            'is_superuser'
        )

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Parolalar eşleşmiyor.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        team_id = validated_data.pop('team_id', None)
        
        user = User.objects.create_user(**validated_data)
        
        if team_id:
            try:
                team = Team.objects.get(id=team_id)
                user.team = team
                user.save()
            except Team.DoesNotExist:
                raise serializers.ValidationError("Geçersiz takım seçimi")
                
        return user

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        team_id = validated_data.pop('team_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        if team_id:
            try:
                team = Team.objects.get(id=team_id)
                instance.team = team
            except Team.DoesNotExist:
                raise serializers.ValidationError("Geçersiz takım seçimi")
                
        instance.save()
        return instance

class TokenSerializer(serializers.Serializer):
   access = serializers.CharField(
       help_text="Access token"
   )
   refresh = serializers.CharField(
       help_text="Refresh token"
   )

class LoginResponseSerializer(serializers.Serializer):
   message = serializers.CharField(
       help_text="İşlem sonucu mesajı"
   )
   tokens = TokenSerializer(
       help_text="JWT token bilgileri"
   )
   user = UserSerializer(
       help_text="Giriş yapan kullanıcı bilgileri"
   )

   def to_representation(self, instance):
       # instance'dan gelen user objesini UserSerializer ile serialize eder
       user_data = UserSerializer(instance['user']).data
       return {
           'message': instance['message'],
           'tokens': instance['tokens'],
           'user': user_data
       }

class LoginRequestSerializer(serializers.Serializer):
   username = serializers.CharField()
   password = serializers.CharField(write_only=True)

class ErrorResponseSerializer(serializers.Serializer):
   error = serializers.CharField()

class MessageResponseSerializer(serializers.Serializer):
   message = serializers.CharField()