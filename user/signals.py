from django.db.models import signals
from django.conf import settings
from django.dispatch import receiver
from django.db import transaction

from user.models import *


@receiver(signals.post_migrate)
@transaction.atomic
def add_default_roles(sender, **kwargs):
    print('me!')
    for role in settings.DEFAULT_ROLES:
        role_obj, created = Role.objects.get_or_create(title=role['title'])
        for permission in role['permissions']:
            state_obj, state_created = State.objects.get_or_create(title=permission['state'])
            role_access, access_created = RoleAccess.objects.get_or_create(role=role_obj, state=state_obj)
            for operate in permission['operates']:
                operate_obj, operate_created = Operate.objects.get_or_create(title=operate)
                Permission.objects.get_or_create(access=role_access, operate=operate_obj)