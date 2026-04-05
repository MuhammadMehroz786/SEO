from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_overview, name="dashboard-overview"),
    path("<int:store_id>/", views.store_dashboard, name="store-dashboard"),
]
