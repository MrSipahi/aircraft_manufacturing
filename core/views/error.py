
from django.views import View

from django.shortcuts import render
from rest_framework.permissions import AllowAny

class ErrorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'error.html', {'error': 'Error'})


    @staticmethod
    def access_denied(request):
        return render(request, 'error.html', {'error': 'Access Denied'})
    