from django.urls import path
from .views import user_profile_view, register, login_user

urlpatterns = [
    path("register/",register,name="register"),
    path("login/",login_user,name="login"),
    path("accounts/",user_profile_view, name="user_profile_view" ),
]