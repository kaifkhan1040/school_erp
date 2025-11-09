from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
# from helpdesk.customadmin.models import Company
import os

class Designation(models.Model):
    name=models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class CustomUser(AbstractUser):
    status_choice=(
        ('watting','Watting'),
        ('approved','Approved'),
        ('rejected','Rejected')
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    status = models.CharField(choices=status_choice,max_length=100,default='watting')
    delete_status = models.BooleanField(default=0)
    # strpass = models.CharField(max_length=255)
    token = models.CharField(max_length=16)
    phone_number=models.CharField(max_length=10,null=True,blank=True)
    image = models.ImageField(upload_to='user_profile/', null=True,blank=True)
    address = models.CharField(max_length=500,null=True,blank=True)
    salary = models.CharField(max_length=500,null=True,blank=True)
    designation = models.ForeignKey(Designation,on_delete=models.SET_NULL,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    zipcode = models.CharField(max_length=8,null=True,blank=True)
    country = models.CharField(max_length=255,null=True,blank=True)
    role = models.CharField(max_length=500,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    doj = models.DateField(null=True,blank=True)
    is_report = models.BooleanField(default=False)
    is_task_recive = models.BooleanField(default=False)
    is_task_create = models.BooleanField(default=False)
    reporting_manager = models.ForeignKey(
        'self',                      # refers to same model
        on_delete=models.SET_NULL,   # keep user if manager deleted
        null=True,
        blank=True,
        related_name='subordinates'  # allows reverse lookup (manager.subordinates.all())
    )

    def __str__(self):
        return self.email

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()
        
    def save(self, *args, **kwargs):
        """ Delete old image when a new one is uploaded """
        try:
            old_user = CustomUser.objects.get(id=self.id)
            if old_user.image and self.image and old_user.image != self.image:
                if os.path.isfile(old_user.image.path):
                    os.remove(old_user.image.path)
        except CustomUser.DoesNotExist:
            pass  

        super().save(*args, **kwargs)


class ForgetPassMailVerify(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    link=models.CharField(max_length=500)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

class UserEmailVerify(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    link = models.CharField(max_length=500)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
    
class UserNumberVerify(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user
    
