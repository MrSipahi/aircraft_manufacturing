from django.urls import path
from .views.inventory import InventoryView,InventoryDetailView
from .views.part import PartView,PartDetailView
from .views.assembly import AssemblyView,AssemblyDetailView
from .views.dashboard import DashboardView
from .views.error import ErrorView
from .views.aircraft import AircraftRequirementView, AvailablePartsView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path('inventory/', InventoryView.as_view(), name='inventory'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),

    path('part/', PartView.as_view(), name='part'),
    path('part/<int:pk>/', PartDetailView.as_view(), name='part_detail'),

    path('assembly/', AssemblyView.as_view(), name='assembly'),
    path('assembly/<int:pk>/', AssemblyDetailView.as_view(), name='assembly_detail'),

    path('aircraft/<int:aircraft_id>/requirements/', AircraftRequirementView.as_view(), name='aircraft_requirements'),
    path('aircraft/<int:aircraft_id>/part_type/<int:part_type_id>/available_parts/', AvailablePartsView.as_view(), name='available_parts'),


    path('permission-denied/', ErrorView.access_denied, name='403'),

]