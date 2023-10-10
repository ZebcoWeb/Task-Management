from django.contrib import admin

from org.models import Organization

class OrgAdmin(admin.ModelAdmin):
    list_display = ['id','title','created_at']
    search_fields = ['title','description',]
    list_per_page = 20
    ordering = ['id']
    
admin.site.register(Organization, OrgAdmin)
