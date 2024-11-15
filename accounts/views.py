# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout,get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import redirect
from core.decorators import check_team_permission
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from .models import Team

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer, 
    ErrorResponseSerializer,
    MessageResponseSerializer,
    UserSerializer,
    TeamSerializer,
    UserCreateUpdateSerializer
)
import json
import logging
logger = logging.getLogger("core")

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    template_name = 'accounts/login.html'

    @swagger_auto_schema(
        operation_summary="Kullanıcı girişi",
        operation_description="Username ve password ile giriş yapar",
        request_body=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer
        }
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Geçersiz veri ",extra={'user': "",'detail': json.dumps(request.data),'path': request.path} )
            return Response(
                ErrorResponseSerializer({"error": "Geçersiz veri"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            logger.info(f"Giriş başarılı",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'message': 'Giriş başarılı',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': user
            }
            
            response = Response(
                LoginResponseSerializer(response_data).data,
                status=status.HTTP_200_OK
            )
            
            # Token'ı cookie'ye ekle
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,  # JavaScript erişimini engelle
                samesite='Lax'  # CSRF koruması
            )
            
            return response
        else:
            logger.warning(f"Geçersiz kullanıcı adı veya şifre",extra={'user': "",'detail': json.dumps(request.data),'path': request.path} )
            return Response(
                ErrorResponseSerializer({"error": "Geçersiz kullanıcı adı veya şifre"}).data,
                status=status.HTTP_401_UNAUTHORIZED
            )

    def get(self, request):
        """GET metodu - Login formunu gösterir"""
        if request.user.id:
            return redirect('dashboard')
        
        return render(request, self.template_name)
            
    
class LogoutView(APIView):
    @swagger_auto_schema(
        operation_summary="Kullanıcı çıkışı",
        operation_description="Mevcut oturumu sonlandırır",
        responses={
            200: MessageResponseSerializer,
        }
    )
    def post(self, request):
        """POST metodu - Kullanıcı çıkışı yapar"""
        logger.info(f"Çıkış isteği atıldı",extra={'user': request.user.username,'detail': request.method,'path': request.path} )
        response = Response({"message": "Çıkış başarılı"})
        response.delete_cookie('access_token')
        return response


class UserView(APIView):
    
    template_name = 'accounts/user_list.html'

    def get_queryset(self, search=None, order_by=None):
        # Datatable için oluşturulan sorgu
        user = self.request.user
        user_model = get_user_model()
        queryset = user_model.objects.select_related('team', 'team__part_type')
        

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
        operation_summary="Kullanıcı Listesi",
        operation_description="Mevcut kullanıcıların listesini döndürür",
        responses={
            200: UserSerializer(many=True),
        }
    )
    @check_team_permission('manage_users')
    def get(self, request):
        """GET metodu - Kullanıcı Listesini döndürür"""
        logger.info(f"Kullanıcı listesi görüntülendi",extra={'user': request.user.username,'detail': request.method,'path': request.path} )

        if request.content_type == 'application/json':
            search = request.GET.get('search_value', '')
            order_column = request.GET.get('order_column', 0)
            order_dir = request.GET.get('order_dir', 'asc')
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))

            columns = ['username', 'mail', 'team', 'is_superuser']
            
            order_by = columns[int(order_column)] if int(order_column) < len(columns) else 'name'
            if order_dir == 'desc':
                order_by = '-' + order_by
            
            queryset = self.get_queryset(search=search, order_by=order_by)

            paginated_queryset = queryset[start:start + length]

            serializer = UserSerializer(paginated_queryset, many=True)
            response_data = {
                "draw": int(request.GET.get('draw', 1)),  
                "recordsTotal": queryset.count(),  
                "recordsFiltered": queryset.count(),  
                "data": serializer.data 
            }

            return Response(response_data)
        else:
            return render(request, self.template_name)
        
    
    @swagger_auto_schema(
        operation_summary="Kullanıcı Oluştur",
        operation_description="Yeni bir kullanıcı oluşturur",
        request_body=UserCreateUpdateSerializer,
        responses={
            201: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        })
    @check_team_permission('manage_users')
    def post(self, request):
        """POST metodu - Yeni kullanıcı oluşturur"""
        serializer = UserCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Kullanıcı oluşturuldu",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
            return Response(
                {"message": "Kullanıcı başarıyla oluşturuldu"},
                status=status.HTTP_201_CREATED
            )
        logger.warning(f"Kullanıcı kaydetme işleminde geçersiz veri",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    


class UserDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Kullanıcı Detay",
        operation_description="Kullanıcı detaylarını döndürür",
        responses={
            200: UserSerializer,
            404: ErrorResponseSerializer
        })
    def get(self, request, user_id):
        """GET metodu - Kullanıcı detaylarını döndürür"""
        try:
            user = get_user_model().objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except get_user_model().DoesNotExist:
            return Response(
                {"error": "Kullanıcı bulunamadı"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_summary="Kullanıcı Güncelle",
        operation_description="Kullanıcı bilgilerini günceller",
        request_body=UserCreateUpdateSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer
        })
    @check_team_permission('manage_users')
    def put(self, request, user_id):
        """PUT metodu - Kullanıcı bilgilerini günceller"""
        try:
            user = get_user_model().objects.get(id=user_id)
            serializer = UserCreateUpdateSerializer(
                user,
                data=request.data,
                partial=True  
            )
            if serializer.is_valid():
                logger.info(f"Kullanıcı güncellendi",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
                serializer.save()
                return Response({"message": "Kullanıcı başarıyla güncellendi"})
            
            logger.warning(f"Kullanıcı güncelleme işleminde geçersiz veri",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except get_user_model().DoesNotExist:
            logger.warning(f"Kullanıcı bulunamadı",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
            return Response(
                {"error": "Kullanıcı bulunamadı"},
                status=status.HTTP_404_NOT_FOUND
            )


    @swagger_auto_schema(
        operation_summary="Kullanıcı Sil",
        operation_description="Kullanıcıyı siler",
        responses={
            200: MessageResponseSerializer,
            404: ErrorResponseSerializer
        })
    @check_team_permission('manage_users')
    def delete(self, request, user_id):
        """DELETE metodu - Kullanıcıyı siler"""
        try:
            user = get_user_model().objects.get(id=user_id)
            # Süper kullanıcıların silinmesini engelle
            if user.is_superuser:
                return Response(
                    {"error": "Süper kullanıcılar silinemez"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.delete()
            logger.info(f"Kullanıcı silindi",extra={'user': request.user.username,'detail': json.dumps(request.data),'path': request.path} )
            return Response({"message": "Kullanıcı başarıyla silindi"})
        except get_user_model().DoesNotExist:
            return Response(
                {"error": "Kullanıcı bulunamadı"},
                status=status.HTTP_404_NOT_FOUND
            )

class TeamListView(APIView):
    @swagger_auto_schema(
        operation_summary="Takım Listesi",
        operation_description="Mevcut takımların listesini döndürür",
        responses={
            200: TeamSerializer(many=True),
        })
    @check_team_permission('manage_users')
    def get(self, request):
        """GET metodu - Takım listesini döndürür"""
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)