from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

class JWTAuthenticationMiddleware:
    """
    API ve HTML sayfaları için JWT token'ı kontrol eden middleware
    Not: Tarayıcı isteklerinde HTTP_AUTHORIZATION header'ı olmadığı için token'ı cookie'den alıyoruz
    Login işleminden sonra token cookie'ye yazılır ve her istekte cookie'den token alınır
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        if  '/accounts/login/' in request.path or '/__debug__/' in request.path:
            return self.get_response(request)

        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            access_token = request.COOKIES.get('access_token')
            if access_token:
                header = f'Bearer {access_token}'
                request.META['HTTP_AUTHORIZATION'] = header
            else:
                return redirect('login')

        try:
            # Token'ı validate et
            token = header.split(' ')[1]
            validated_token = self.jwt_auth.get_validated_token(token)
            
            # User'ı ilişkili verilerle birlikte tek sorguda al
            User = get_user_model()
            user = User.objects.select_related('team', 'team__part_type').get(
                id=validated_token['user_id']
            )
            request.user = user

        except Exception as e:
            return redirect('login')
        
        return self.get_response(request)