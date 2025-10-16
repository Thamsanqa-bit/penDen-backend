from django.urls import path
from . import views

urlpatterns = [
    path('api/checkout/', views.checkout, name='checkout'),
]