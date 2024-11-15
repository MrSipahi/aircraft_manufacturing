from django.contrib import admin
from .models.part import Part, PartType
from .models.aircraft import Aircraft, AircraftRequirement
from .models.assembly import Assembly

admin.site.register(Part)
admin.site.register(PartType)
admin.site.register(Aircraft)
admin.site.register(Assembly)
admin.site.register(AircraftRequirement)




