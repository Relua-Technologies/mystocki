from django.urls import path
from apps.core.views.sale import SaleListView, SaleCreateView, SaleUpdateView


name = 'sale'
urlpatterns = [
    path('list/', SaleListView.as_view(), name=f'{name}_list'),
    path('create/', SaleCreateView.as_view(), name=f'{name}_create'),
    path('update/<slug:pk>/', SaleUpdateView.as_view(), name=f'{name}_update'),
]