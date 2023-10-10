from django.contrib import admin
from user.models import (
    Role,
    UserRole,
    Token,
    Permission,
    RoleAccess,
    State,
    Operate,
    User,
)

class RoleAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    search_fields = ['title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['title']

class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id','user','role']
    search_fields = ['user__username','role__title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['user','role']

class TokenAdmin(admin.ModelAdmin):
    list_display = ['id','user','player_id','created']
    search_fields = ['user__username','player_id']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['user']

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id','access','operate']
    search_fields = ['access__role__title','operate__title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['access','operate']

class RoleAccessAdmin(admin.ModelAdmin):
    list_display = ['id','role','state']
    search_fields = ['role__title','state__title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['role','state']

class StateAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    search_fields = ['title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['title']

class OperateAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    search_fields = ['title']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['title']

class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username','email','first_name','last_name','is_active','is_staff','is_superuser']
    search_fields = ['username','email','first_name','last_name']
    list_per_page = 20
    ordering = ['id']
    list_filter = ['is_active','is_staff','is_superuser']
    
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(RoleAccess, RoleAccessAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Operate, OperateAdmin)
admin.site.register(User, UserAdmin)


