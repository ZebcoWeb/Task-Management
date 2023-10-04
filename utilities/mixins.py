from django.db import models


class SoftDelete(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        HIDE = "HIDE"
        DELETED = "DELETED"
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        abstract = True

    def delete(self):
        self.status = self.Status.DELETED
        self.save()
    
    def hide(self):
        self.status = self.Status.HIDE
        self.save()
    
    def recycle(self):
        self.status = self.Status.ACTIVE
        self.save()