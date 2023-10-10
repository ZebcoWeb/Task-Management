from django.contrib import admin

from request.models import Request



class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'requested_role', 'organization', 'status', 'created_at']
    search_fields = ['requested_role', 'status']
    list_per_page = 20
    ordering = ['id']


admin.site.register(Request, RequestAdmin)