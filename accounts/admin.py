from django.contrib import admin
from .models import CustomUser,Team,TeamPermission

admin.site.register(CustomUser)
admin.site.register(Team)
admin.site.register(TeamPermission)
