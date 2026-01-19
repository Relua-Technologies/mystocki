from django.urls import path
from apps.core.views.overview import OverviewView
from apps.core.views.overview.api import OverviewStatsAPIView


name = 'overview'
urlpatterns = [
    path('', OverviewView.as_view(), name=name),
    path('api/stats/', OverviewStatsAPIView.as_view(), name=f'{name}_api_stats'),
]

