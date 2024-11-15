# core/views/inventory.py
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import json
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render, get_object_or_404
from ..models.inventory import Inventory
from ..models.part import Part
from ..models.aircraft import AircraftRequirement
from ..serializers.inventory import InventorySerializer,InventoryPatchSerializer
from django.db.models import Q
from django.db import models
from core.decorators import check_team_permission

import logging

logger = logging.getLogger("core")

class InventoryView(APIView):
    template_name = 'core/inventory_list.html'

    def get_queryset(self, search=None, order_by=None):
        # Datatable için oluşturulan sorgu
        user = self.request.user
        
        queryset = Inventory.objects.select_related(
            'part_type',
            'aircraft_type'
        )
        
        # User kontrollerini middleware verisiyle yap (User için ekstra istek atmaması için)
        if user.is_superuser:
            pass 
        elif not user.team:
            raise PermissionDenied("Kullanıcının takımı bulunmuyor.")
        elif not user.team.is_assembly_team:
            queryset = queryset.filter(part_type_id=user.team.part_type_id) 

        if search:
            queryset = queryset.filter(
                Q(part_type__name__icontains=search) |
                Q(aircraft_type__name__icontains=search)
            )

        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset


    def get_missing_parts(self):
        requirements = (
            AircraftRequirement.objects
            .select_related('aircraft_type', 'part_type')
            .values(
                'aircraft_type__name', 
                'part_type__name', 
                'quantity', 
                'aircraft_type_id', 
                'part_type_id'
            )
        )

        result = {}
        for req in requirements:
            aircraft = req['aircraft_type__name']
            part_count = Part.objects.filter(
                aircraft_type_id=req['aircraft_type_id'],
                type_id=req['part_type_id'],
                is_used=False
            ).count()
            
            missing = req['quantity'] - part_count
            if missing > 0:
                if aircraft not in result:
                    result[aircraft] = []
                result[aircraft].append({
                    'part': req['part_type__name'],
                    'quantity': missing
                })

        return result

    @swagger_auto_schema(
        operation_summary="Envanter listesi  döndürür",
        operation_description="Kullanıcının yetkisine göre envanter listesini  döndürür",
        responses={200: InventorySerializer(many=True)}
    )
    @check_team_permission('view_inventory')
    def get(self, request):
        """GET metodu - Envanter Listesini döndürür - Content-Type'a göre JSON veya HTML döner - Datatable için uygun"""
        
        logger.info('Envanter Listesi görüntülenme istegi atildi.',extra={'user': request.user.username,'detail': request.method,'path': request.path})

        if request.content_type == 'application/json':
            search = request.GET.get('search_value', '')
            order_column = request.GET.get('order_column', 0)
            order_dir = request.GET.get('order_dir', 'asc')
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))

            columns = ['part_type', 'aircraft_type', 'quantity', 'minimum_quantity','updated_at']
            

            order_by = columns[int(order_column)] if int(order_column) < len(columns) else 'name'
            if order_dir == 'desc':
                order_by = '-' + order_by
            
            queryset = self.get_queryset(search=search, order_by=order_by)

            paginated_queryset = queryset[start:start + length]

            serializer = InventorySerializer(paginated_queryset, many=True)
            response_data = {
                "draw": int(request.GET.get('draw', 1)),  
                "recordsTotal": queryset.count(),  
                "recordsFiltered": queryset.count(),  
                "data": serializer.data 
            }

            return Response(response_data)
        else:
            missing_parts = self.get_missing_parts()
            print(missing_parts)
            return render(request, self.template_name, {'missing_parts': missing_parts})
    


    
    
    


class InventoryDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Envanter detayını döndürür",
        operation_description="Envanter detayını döndürür",
        responses={200: InventorySerializer}
    )
    def get(self, request, pk):
        """GET metodu - Tekil kayıt döndürür"""
        inventory = get_object_or_404(Inventory, pk=pk)
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_summary="Envanter güncelleme",
        operation_description="Envanterin miktarını günceller",
        request_body=InventoryPatchSerializer,
        responses={200: InventorySerializer}
    )
    @check_team_permission('manage_inventory')
    def patch(self, request, pk):
        """PATCH metodu - Parça güncelleme"""
        
        inventory = get_object_or_404(Inventory, pk=pk)

        # Serializer ile gelen veriyi doğrula ve sadece 'minimum_quantity' alanını güncelle
        serializer = InventoryPatchSerializer(inventory, data=request.data, partial=True)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info('Envanter güncelleme işlemi tamamlandı.',extra={'user': request.user.username,'detail': json.dumps(InventorySerializer(inventory).data),'path': request.path})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.info('Envanter güncelleme işlemi tamamlanamadı.',extra={'user': request.user.username,'detail': json.dumps(serializer.errors),'path': request.path})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)