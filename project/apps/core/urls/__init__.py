from django.urls import path
from django.shortcuts import redirect
from apps.core.views.overview import OverviewView
from apps.core.urls.managers import AppURLManager


class UrlManager(AppURLManager):
    urls_folder = 'apps.core.urls'

urlpatterns = [
    path('', lambda request: redirect('core:sale_list'), name='root_redirect'),
] + UrlManager().urlpatterns