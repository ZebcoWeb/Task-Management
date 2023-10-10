from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

from org.models import Organization
from utilities.mixins import SoftDelete


class CustomUserManager(UserManager):
    def create_superuser(self, username, password=None, **kwargs):
        user = self.model(
            username=username, 
            is_staff=True, 
            is_superuser=True, 
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user
    

class User(AbstractUser, SoftDelete):
    # groups = None
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=130)
    username = models.CharField(max_length=100, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='user_creator', null=True, editable=False)
    modified_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='user_modifier', null=True)
    
    login_error = models.IntegerField(default=0)
    deactive_count = models.IntegerField(default=0)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "users"
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bearer_token',)
    key = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    remote_addr = models.TextField()
    user_agent = models.TextField()
    player_id = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "token"
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        

class Role(models.Model):
    title = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"

class UserRole(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        db_table = "user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
    
    def create(self, validated_data):
        user = validated_data.get('user')
        role = validated_data.get('role')
        return self.objects.get_or_create(user=user, role=role)

        
class Permission(models.Model):
    access = models.ForeignKey("RoleAccess", on_delete=models.CASCADE, related_name="permissions")
    operate = models.ForeignKey("Operate", on_delete=models.CASCADE, related_name="permissions", null=True, blank=True)
    
    class Meta:
        db_table = "permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

class RoleAccess(models.Model):
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="role_accesses")
    state = models.ForeignKey("State", on_delete=models.CASCADE, related_name="accesses")
    
    class Meta:
        db_table = "role_accesses"
        verbose_name = "Role Access"
        verbose_name_plural = "Role Accesses"
    
    def create(self, validated_data):
        role = validated_data.get('role')
        state = validated_data.get('state')
        return self.objects.get_or_create(role=role, state=state)
    
class State(models.Model):
    title = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = "states"
        verbose_name = "State"
        verbose_name_plural = "States"

    def __str__(self) -> str:
        return self.title

class Operate(models.Model):
    title = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = "operates"
        verbose_name = "Operate"
        verbose_name_plural = "Operates"

    def __str__(self) -> str:
        return self.title