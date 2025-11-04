from django.urls import path
from apps.authentication.views import SingInView, signout_view

urlpatterns = [
    path('signin/', SingInView.as_view(), name='sign_in'),
    path('signout/', signout_view, name='sign_out'),
] 