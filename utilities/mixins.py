from django.db import models


class SoftDelete(models.Model):
    class Status(models.TextChoices):
        PUBLISH = 1
        UNPUBLISH = 0
        TRASH = -1
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.PUBLISH)

    class Meta:
        abstract = True