from django.contrib import admin

from task.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title','description','functor','deadline','finished_at','created_at']
    search_fields = ['title','description','functor__username']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['title','description','functor','deadline','finished_at','created_at']
    
admin.site.register(Task, TaskAdmin)
