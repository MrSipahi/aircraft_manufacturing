from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render, get_object_or_404,redirect
from django.core.exceptions import PermissionDenied
from ..models.aircraft import Aircraft
from ..models.assembly import Assembly
from ..serializers.assembly import AssemblySerializer, AssemblyCreateSerializer
from ..models.part import Part
from django.db.models import Q,Prefetch
from django.db import transaction

from core.decorators import check_team_permission

import logging
logger = logging.getLogger("core")

class AssemblyView(APIView):
    template_name = 'core/assembly_list.html'

    def get_queryset(self, search=None, order_by=None):
        # Datatable için oluşturulan sorgu

        # İlişkili alanları tek sorguda alır, sorgu optimizasyonu için önemli
        queryset = Assembly.objects.select_related(
            'aircraft_type',
            'assembled_by',
            'assembled_by__team'
        ).prefetch_related(
            Prefetch(
                'parts',
                queryset=Part.objects.select_related(
                    'type',
                    'aircraft_type',
                    'created_by',
                    'created_by__team'
                ).order_by('-created_at')
            )
        )
        
        if search:
            queryset = queryset.filter(
                Q(aircraft_type__name__icontains=search) |
                Q(assembled_by__username__icontains=search) |
                Q(notes__icontains=search)
            )

        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset

    @swagger_auto_schema(
        operation_summary="Montaj listesi görüntüleme",
        operation_description="Montajların listesini döndürür",
        responses={200: AssemblySerializer(many=True)}
    )
    @check_team_permission('view_assembly')
    def get(self, request):
        """GET metodu - Montaj Listesini döndürür - Content-Type'a göre JSON veya HTML döner - Datatable için uygun"""

        logger.info(f"Montaj görüntülenme istegi atildi.",extra={'user': request.user.username,'detail': request.method,'path': request.path} )

        if request.content_type == 'application/json' or request.GET.get('format') == 'json':
            search = request.GET.get('search_value', '')
            order_column = request.GET.get('order_column', 0)
            order_dir = request.GET.get('order_dir', 'asc')
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))

            columns = ['aircraft_type__name', 'assembled_by__username', 'assembled_at', 'is_complete']
            
            order_by = columns[int(order_column)] if int(order_column) < len(columns) else 'assembled_at'
            if order_dir == 'desc':
                order_by = '-' + order_by
            
            queryset = self.get_queryset(search=search, order_by=order_by)
            total_count = queryset.count()
            
            paginated_queryset = queryset[start:start + length]
            serializer = AssemblySerializer(paginated_queryset, many=True)
            
            response_data = {
                "draw": int(request.GET.get('draw', 1)),
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": serializer.data
            }

            return Response(response_data)
        else:
            aircraft_types = Aircraft.objects.all()
            return render(request, self.template_name, {'aircraft_types': aircraft_types})
        

    @swagger_auto_schema(
        operation_summary="Yeni montaj oluşturur",
        operation_description="Seçilen parçalarla yeni bir montaj oluşturur",
        request_body=AssemblyCreateSerializer,
        responses={201: AssemblySerializer()}
    )
    @check_team_permission('manage_assembly')
    def post(self, request):
        serializer = AssemblyCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            """
            Montaj oluşturma işlemleri
            Transaction kullanarak verilerin tutarlılığını sağlar, aynı zamanda aynı anda birden fazla işlem yapılmasını engellemek için kullanıldı
            """
            logger.info(f"Montaj oluşturma isteği atıldı.",extra={'user': request.user.username,'detail': request.method,'path': request.path} )
            try:
                with transaction.atomic():  
                    assembly = serializer.save(
                        assembled_by=request.user,
                        is_complete=True
                    )

                    for part in serializer.validated_data['parts']:
                        part.is_used = True
                        part.save()

                    return Response(
                        AssemblySerializer(assembly).data,
                        status=status.HTTP_201_CREATED
                    )
            except Exception as e:
                logger.error(f"Montaj oluşturma işlemi sırasında hata oluştu.",extra={'user': request.user.username,'detail': str(e),'path': request.path} )
                return Response(
                    {"error": "Montaj oluşturulurken bir hata oluştu."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

class AssemblyDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Montaj detayı görüntüleme",
        operation_description="Montaj detayını döndürür",
        responses={200: AssemblySerializer()}
    )
    @check_team_permission('view_assembly')
    def get(self, request, pk):
        """GET metodu - Tekil kayıt döndürür"""

        logger.info(f"Montaj detay görüntüleme isteği atıldı.",extra={'user': request.user.username,'detail': request.method,'path': request.path} )

        # Tüm ilişkili verileri tek sorguda alır, sorgu optimizasyonu için önemli
        assembly = get_object_or_404(
            Assembly.objects
            .select_related(
                'aircraft_type',
                'assembled_by',
                'assembled_by__team'
            )
            .prefetch_related(
                Prefetch(
                    'parts',
                    queryset=Part.objects.select_related(
                        'type',
                        'aircraft_type',
                        'created_by',
                        'created_by__team'
                    ).order_by('-created_at')
                )
            ),
            pk=pk
        )
        serializer = AssemblySerializer(assembly)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Montaj siler",
        operation_description="Montajı siler",
        responses={204: "No Content"}
    )
    @check_team_permission('manage_assembly')
    def delete(self, request, pk):
        assembly = get_object_or_404(Assembly, pk=pk)
            
        # Parçaları kullanılmamış olarak işaretle
        for part in assembly.parts.all():
            part.is_used = False
            part.save()
            
        assembly.delete()
        logger.info('Montaj silme işlemi başarılı.',extra={'user': request.user.username,'detail': f"Montaj id:{pk}",'path': request.path})
        return Response(status=status.HTTP_204_NO_CONTENT)