# core/views/aircraft.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from ..models.aircraft import Aircraft
from ..models.part import Part
from ..serializers.aircraft import AircraftRequirementSerializer, AvailablePartSerializer
from core.decorators import check_team_permission


import logging
logger = logging.getLogger("core")

class AircraftRequirementView(APIView):


    @swagger_auto_schema(
        operation_summary="Uçak gereksinimleri",
        operation_description="Belirtilen uçak için gerekli parça tiplerini ve miktarlarını döndürür",
        responses={200: AircraftRequirementSerializer(many=True)}
    )
    @check_team_permission('view_assembly')
    def get(self, request, aircraft_id):
        """GET metodu - Uçak gereksinimlerini döndürür"""
        
        logger.info(f"Uçak gereksinimleri istendi",extra={'user': request.user.username,'detail': f"Aircraft : {aircraft_id}",'path': request.path} )

        aircraft = get_object_or_404(Aircraft, pk=aircraft_id)
        requirements = aircraft.requirements.all()
        serializer = AircraftRequirementSerializer(requirements, many=True)
        
        return Response(serializer.data)

class AvailablePartsView(APIView):


    @swagger_auto_schema(
        operation_summary="Kullanılabilir parçalar",
        operation_description="Belirtilen uçak ve parça tipi için kullanılabilir parçaları döndürür",
        responses={200: AvailablePartSerializer(many=True)}
    )
    @check_team_permission('view_assembly')
    def get(self, request, aircraft_id, part_type_id):
        """GET metodu - Kullanılabilir parçaları döndürür"""
        
        logger.info(f"Kullanılabilir parçalar istendi",extra={'user': request.user.username,'detail': f"Aircraft : {aircraft_id}, Part Type : {part_type_id}",'path': request.path} )
        # Kullanılmamış ve belirtilen uçak tipine ait parçaları getir
        available_parts = Part.objects.filter(
            aircraft_type_id=aircraft_id,
            type_id=part_type_id,
            is_used=False
        )
        
        serializer = AvailablePartSerializer(available_parts, many=True)
        return Response(serializer.data)