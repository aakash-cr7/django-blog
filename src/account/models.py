from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    pass
    class Meta:
        unique_together = ('email',)
        verbose_name = 'User'
