from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect

import logging

logger = logging.getLogger("core")
def check_team_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.has_team_permission(permission):
                logger.warning(f"Kullanıcı  bu işlemi yapmaya yetkili değil.",extra={'user': request.user.username,'detail': request.method,'path': request.path} )
                if request.content_type == 'application/json':
                    return Response(
                        {"error": "Bu işlem için yetkiniz yok."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                return redirect('403')
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator