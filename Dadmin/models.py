# Create your models here.
# models.py
from django.db import models

class AdminUser(models.Model):  
    email = models.EmailField(unique=True, blank=False, null=False)  
    password = models.CharField(max_length=128, blank=False, null=False)  

    def _str_(self):  
        return self.email
