from django.urls import path
from .views import user_profile_view, register, login_user

urlpatterns = [
    path("api/register/",register,name="register"),
    path("api/login/",login_user,name="login"),
    path("api/accounts/",user_profile_view, name="user_profile_view" ),
]