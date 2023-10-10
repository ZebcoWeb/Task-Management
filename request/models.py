from django.db import models

from org.models import Organization
from user.models import User


class Request(models.Model):
    class Status(models.TextChoices):
        PENDING = 0
        ACCEPTED = 1
        REJECTED = -1
    class RequestedRole(models.TextChoices):
        ORG_MANAGER = 1
        ORG_EMPLOYEE = 2

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.PENDING)
    requested_role = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True, related_name="requests")
    
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "requests"
        verbose_name = "Request"
        verbose_name_plural = "Requests"