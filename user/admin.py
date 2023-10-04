# from django.contrib import admin
# from users.models import (
#     Role,
#     UserRole,
#     Token,
#     Permission,
#     RoleAccess,
#     State,
#     Operate,
#     User,
#     PromotionRequest
# )


# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'organization')
#     list_filter = ('organization',)
#     search_fields = ('username',  'organization')
#     ordering = ('username', 'organization')

#     fieldsets = (
#         (None, {
#             'fields': ('username', 'organization')
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'organization'),
#         }),
#     )

#     filter_horizontal = ()

# class RoleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     list_filter = ('name',)
#     search_fields = ('name',)
#     ordering = ('name',)

#     fieldsets = (
#         (None, {
#             'fields': ('name',)
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('name',),
#         }),
#     )

#     filter_horizontal = ()

# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'role')
#     list_filter = ('user', 'role')
#     search_fields = ('user', 'role')
#     ordering = ('user', 'role')

#     fieldsets = (
#         (None, {
#             'fields': ('user', 'role')
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('user', 'role'),
#         }),
#     )

#     filter_horizontal = ()

# class TokenAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created')
#     list_filter = ('user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created')
#     search_fields = ('user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created')
#     ordering = ('user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created')

#     fieldsets = (
#         (None, {
#             'fields': ('user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created')
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('user', 'key', 'refresh_token', 'remote_addr', 'user_agent', 'player_id', 'created'),
#         }),
#     )

#     filter_horizontal = ()

# class PermissionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'access', 'operate')
#     list_filter = ('access', 'operate')
#     search_fields = ('access', 'operate')
#     ordering = ('access', 'operate')

#     fieldsets = (
#         (None, {
#             'fields': ('access', 'operate')
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('access', 'operate'),
#         }),
#     )

#     filter_horizontal = ()

# class RoleAccessAdmin(admin.ModelAdmin):
#     list_display = ('id', 'role', 'state')
#     list_filter = ('role', 'state')
#     search_fields = ('role', 'state')
#     ordering = ('role', 'state')

#     fieldsets = (
#         (None, {
#             'fields': ('role', 'state')
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('role', 'state'),
#         }),
#     )

#     filter_horizontal = ()

# class StateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title')
#     list_filter = ('title',)
#     search_fields = ('title',)
#     ordering = ('title',)

#     fieldsets = (
#         (None, {
#             'fields': ('title',)
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('title',),
#         }),
#     )

#     filter_horizontal = ()

# class OperateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title')
#     list_filter = ('title',)
#     search_fields = ('title',)
#     ordering = ('title',)

#     fieldsets = (
#         (None, {
#             'fields': ('title',)
#         }),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('title',),
#         }),
#     )

#     filter_horizontal = ()


# admin.site.register(User, AuthorAdmin)
# admin.site.register(Role, RoleAdmin)
# admin.site.register(UserRole, UserRoleAdmin)
# admin.site.register(Token, TokenAdmin)
# admin.site.register(Permission, PermissionAdmin)
# admin.site.register(RoleAccess, RoleAccessAdmin)
# admin.site.register(State, StateAdmin)
# admin.site.register(Operate, OperateAdmin)