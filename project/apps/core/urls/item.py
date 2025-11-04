from django.urls import path
from apps.core.views.item import ItemListView, ItemCreateView, ItemUpdateView

name = 'item'
urlpatterns = [
    path('list/', ItemListView.as_view(), name=f'{name}_list'),
    path('create/', ItemCreateView.as_view(), name=f'{name}_create'),
    path('update/<slug:pk>/', ItemUpdateView.as_view(), name=f'{name}_update'),
]