from django.urls import path
from .views import user_profile_view

urlpatterns = [
    path("api/accounts/",user_profile_view, name="user_profile_view" ),
]