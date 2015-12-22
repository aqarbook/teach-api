from django.contrib.auth.models import User
from django.db import models

# Create your models here.



class UserCredlyProfile(models.Model):

    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=400, null=False, blank=False)
    refresh_token = models.CharField(max_length=400, null=False, blank=False)
    token_created = models.DateTimeField(auto_now_add=True)

