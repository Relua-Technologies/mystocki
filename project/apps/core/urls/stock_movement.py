from django.urls import path
from apps.core.views.stock_movement import StockMovementListView, StockMovementCreateView, StockMovementUpdateView

name = 'stock_movement'
urlpatterns = [
    path('list/', StockMovementListView.as_view(), name=f'{name}_list'),
    path('create/', StockMovementCreateView.as_view(), name=f'{name}_create'),
    path('update/<slug:pk>/', StockMovementUpdateView.as_view(), name=f'{name}_update'),
]