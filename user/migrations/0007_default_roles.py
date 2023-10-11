from django.db import migrations
from django.conf import settings


from user.models import Role, State, Operate, Permission, RoleAccess


def add_default_roles(apps, schema_editor):
    for role in settings.DEFAULT_ROLES:
        role_obj, created = Role.objects.get_or_create(title=role['title'])
        for permission in role['permissions']:
            state_obj, state_created = State.objects.get_or_create(title=permission['state'])
            role_access, access_created = RoleAccess.objects.get_or_create(role=role_obj, state=state_obj)
            for operate in permission['operates']:
                operate_obj, operate_created = Operate.objects.get_or_create(title=operate)
                Permission.objects.get_or_create(access=role_access, operate=operate_obj)
                


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_user_organization'),
    ]

    operations = [
        migrations.RunPython(add_default_roles),
    ]