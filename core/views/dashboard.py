
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render
from rest_framework.permissions import AllowAny
from ..models.assembly import Assembly
from ..models.part import Part
from accounts.models import Team

import logging
logger = logging.getLogger("core")

class DashboardView(APIView):
    def get(self, request):
        logger.info(f"Anasayfa görüntülendi.",extra={'user': request.user.username,'detail': request.method,'path': request.path} )
        context = {
            'total_aircrafts': Assembly.objects.filter(is_complete=True).count(),
            'total_parts': Part.objects.count(),
            'total_teams': Team.objects.count(),
            'total_assemblies': Assembly.objects.count(),
        }
        return render(request, 'home.html' , context)