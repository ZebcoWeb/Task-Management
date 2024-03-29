import functools

from rest_framework import status
from rest_framework.response import Response

from user.models import *



def execute_with_permission(state, operate):
    def decorator(func):
        @functools.wraps(func)
        def check_permission(self, request, *args, **kwargs):
            user = request.user
            chk = False
            
            if (not chk) and user.pk:
                access = True

                if state == "user":
                    user_id = kwargs.get('pk', None)

                    if operate in ["update", "read"]:
                        if user.pk == user_id:
                            chk = True
                    elif operate == "delete":
                        if user.pk == user_id:
                            chk = False
                            access = False
                    elif operate in ["status"]:
                        user_ids = request.data.get('ids', None)
                        if user.pk in user_ids:
                            chk = False
                            access = False
                elif state == "operate":
                    pass
                elif state == "state":
                    pass
                elif state == "role":
                    pass
                elif state == "userrole":
                    pass
                
                if access and not chk:
                    roles = Role.objects.filter(
                        role_accesses__state__title=state,
                        role_accesses__permissions__operate__title=operate
                    ).distinct()

                    if roles:
                        user_role = UserRole.objects.filter(user=user, role__in=roles)

                        if user_role:
                            chk = True
            if chk:
                return func(self, request, *args, **kwargs)
            elif user.pk:
                return Response(
                    {
                        "code": "900",
                        "message": "Forbidden",
                        "detail": "Permission denied",
                    }, status.HTTP_403_FORBIDDEN)
            else:
                return Response(
                    {"code": "899", "message": "User not recognized"},
                    status.HTTP_401_UNAUTHORIZED)

        return check_permission
    return decorator