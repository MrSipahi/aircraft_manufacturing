from django.urls import path
from .views import LoginView, LogoutView,UserView,UserDetailView,TeamListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
   path('login/', LoginView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(), name='logout'),
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

   path('user/', UserView.as_view(), name='user'),
   path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
   path('teams/', TeamListView.as_view(), name='teams'),
]