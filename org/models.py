from django.db import models

from utilities.mixins import SoftDelete




class Organization(SoftDelete):
    title = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organizations"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"