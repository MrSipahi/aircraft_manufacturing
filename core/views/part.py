from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render, get_object_or_404, redirect
from ..models.part import Part
from ..models.aircraft import Aircraft

from django.db.models import Q


from ..serializers.part import PartSerializer, PartCreateSerializer
from core.decorators import check_team_permission


from django.core.exceptions import PermissionDenied
import json

import logging
logger = logging.getLogger("core")

class PartView(APIView):
    template_name = 'core/part_list.html'


    def get_queryset(self, search=None, order_by=None):
        # Datatable için oluşturulan sorgu

        user = self.request.user
        
        # İlişkili alanları tek sorguda alır, sorgu optimizasyonu için önemli
        queryset = Part.objects.select_related(
            'type',
            'aircraft_type',
            'created_by',
            'created_by__team'
        )
        
        # Kullanıcının yetkisine göre parça getirmesi için gerekli kontroller yapılır
        if user.is_superuser:
            pass 
        elif not user.team:
            raise PermissionDenied("Kullanıcının takımı bulunmuyor.")
        elif not user.team.is_assembly_team:
            queryset = queryset.filter(type_id=user.team.part_type_id) 
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(type__name__icontains=search) |
                Q(aircraft_type__name__icontains=search)
            )

        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset

    @swagger_auto_schema(
        operation_summary="Parça listesi görüntüleme",
        operation_description="Kullanıcının yetkisine göre parça listesini döndürür",
        responses={200: PartSerializer(many=True)}
    )
    @check_team_permission('view_part')
    def get(self, request):
        """GET metodu - Parça Listesini döndürür - Content-Type'a göre JSON veya HTML döner - Datatable için uygun"""
        logger.info('Parca Listesi görüntülenme istegi atildi.',extra={'user': request.user.username,'detail': request.method,'path': request.path})
        if request.content_type == 'application/json':
            search = request.GET.get('search_value', '')
            order_column = request.GET.get('order_column', 0)
            order_dir = request.GET.get('order_dir', 'asc')
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))

            columns = ['name', 'type__name', 'aircraft_type__name', 'created_by', 'created_at','status']
            
            order_by = columns[int(order_column)] if int(order_column) < len(columns) else 'name'
            if order_dir == 'desc':
                order_by = '-' + order_by
            
            queryset = self.get_queryset(search=search, order_by=order_by)

            paginated_queryset = queryset[start:start + length]

            serializer = PartSerializer(paginated_queryset, many=True)
            response_data = {
                "draw": int(request.GET.get('draw', 1)),  
                "recordsTotal": queryset.count(),  
                "recordsFiltered": queryset.count(),  
                "data": serializer.data 
            }

            return Response(response_data)
        else:
            aircraft = Aircraft.objects.all()

            return render(request, self.template_name, {'aircrafts': aircraft,'part_type':request.user.team.part_type})
        

    @swagger_auto_schema(
        operation_summary="Yeni parça üretir",
        operation_description="Kullanıcının takımına uygun yeni parça üretir",
        request_body=PartCreateSerializer,
        responses={201: PartSerializer()}
    )
    @check_team_permission('create_part')
    def post(self, request):
        """POST metodu - Yeni parça üretir"""
        
        logger.info('Parca eklenme istegi atildi.',extra={'user': request.user.username,'detail': request.method,'path': request.path})

        serializer = PartCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            part = serializer.save(created_by=request.user)
            logger.info('Parca ekleme islemini tamamladi.',extra={'user': request.user.username,'detail': json.dumps(PartSerializer(part).data),'path': request.path})

            return Response(
                PartSerializer(part).data,
                status=status.HTTP_201_CREATED
            )
        
        logger.info('Parça validasyon işlemini tamamlayamadı.',extra={'user': request.user.username,'detail': json.dumps(serializer.errors),'path': request.path})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
class PartDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Parça detay görüntüleme",
        operation_description="Kullanıcının yetkisine göre parça detayını döndürür",
        responses={200: PartSerializer(many=True)}
    )
    @check_team_permission('view_part')
    def get(self, request, pk):
        """GET metodu - Tekil parça detayını döndürür"""

        part = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = PartSerializer(part)
        
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_summary="Parça siler",
        operation_description="Kullanılmamış parçayı siler",
        responses={204: "No Content"}
    )
    @check_team_permission('delete_part')
    def delete(self, request, pk):
        """DELETE metodu - Parçayı siler"""
        part = get_object_or_404(Part, pk=pk)
        
        if part.is_used:
            return Response(
                {"error": "Kullanılmış parça silinemez."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not request.user.is_superuser and part.type != request.user.team.part_type:
            logger.error('Bu parçayı silme yetkiniz yok.',extra={'user': request.user.username,'detail': f"Parça id:{pk}",'path': request.path})
            return Response(
                {"error": "Bu parçayı silme yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        part.delete()
        logger.info('Parca silme islemi basarili.',extra={'user': request.user.username,'detail': f"Parça id:{pk}",'path': request.path})
        return Response(status=status.HTTP_204_NO_CONTENT)

    

        