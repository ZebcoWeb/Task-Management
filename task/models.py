from django.db import models

from user.models import User
from utilities.mixins import SoftDelete




class Task(SoftDelete):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    functor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='task_functor')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='task_creator', editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='task_modifier')

    deadline = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'