from django.db import models

from django.contrib.auth.models import AbstractUser,AbstractBaseUser,PermissionsMixin

from django.utils import timezone

from .managers import UserModelManager


class CustomUser(AbstractBaseUser, PermissionsMixin):

    username=models.CharField(max_length=50,unique=True)

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    hoppy=models.CharField(max_length=50,default='sleeping')
    
    

    REQUIRED_FIELDS=['hoppy']

    USERNAME_FIELD  = 'username'



    objects = UserModelManager()


    def __str__(self):

        return f'{self.username} like {self.hoppy}'

   


class SocialAccount(models.Model):

    platform_name=models.CharField(max_length=50)

    uid_key=models.BigIntegerField()

    account_name=models.CharField(max_length=60)

    url=models.URLField()

    def __str__(self) -> str:

        
        return self.accont_name

