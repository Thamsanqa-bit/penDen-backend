from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=False, null=False)
    email = models.EmailField(unique=True, default="email", blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False, default="")
    password = models.CharField(max_length=255, default="password", blank=False, null=False)

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return self.user.username
