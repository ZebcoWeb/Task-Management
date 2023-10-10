from datetime import datetime
import jwt

from rest_framework import status
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from user.models import UserRole, User, Role
from request.models import Request
from utilities.exceptions import ProjectException

def get_dict_data(data):
    from django.http import QueryDict

    if type(data) is QueryDict:
        return {
            k: data.getlist(k) if len(data.getlist(k)) > 1 else v
            for k, v in data.items()
        }
    elif type(data) is dict:
        return data
    return {}


def get_player_id(request): 
    meta       = request.META  
    real_ip    = meta.get('HTTP_X_REAL_IP','')
    forwarded_server = meta.get('HTTP_X_FORWARDED_SERVER','')
    remote_addr = meta.get('REMOTE_ADDR','')
    mobile     = meta.get('HTTP_SEC_CH_UA_MOBILE','')
    platform   = meta.get('HTTP_SEC_CH_UA_PLATFORM','')
    session_id = meta.get('HTTP_USER_AGENT','HTTP_USER_AGENT')
    session_id = session_id.replace(' ','_').replace('"','').replace('(','').replace(')','').replace('/','').replace('\\','').replace(';','').replace(',','_').replace('.','_').strip()
    
    player_id = '_'.join([real_ip,forwarded_server,remote_addr,mobile,platform,session_id])
    player_id = player_id.replace(' ','_').replace('"','').replace('(','').replace(')','').replace('/','').replace('\\','').replace(';','').replace(',','_').replace('.','_').strip()
    return player_id, remote_addr, session_id

def get_user(context):
    if context:
        try:
            if 'request' in context:
                request = context['request']
                if request:
                    if request.auth:
                        return request.auth.user
                    elif request.user:
                        return request.user
        except:
            request = context
            if request.auth:
                return request.auth.user
            elif request.user:
                return request.user
    return None

def generate_new_token(user_id, username, player_id, expires_in, grant_type):
    unlimited = False
    if grant_type == 'refresh_token':
        unlimited = settings.REFRESH_TOKEN_UNLIMITED
    token = jwt.encode({
        'grant_type': grant_type,           
        'user_id':   user_id,
        'username': username,           
        'player_id': player_id,
        'unlimited': unlimited,
        'created_at': datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'),
        'expires_at': (datetime.utcnow() + expires_in).strftime('%B %d %Y - %H:%M:%S'),
    }, key=settings.SECRET_KEY, algorithm=settings.SECRET_ALGORITM)   
    return token

def get_data(data: list, pagination: tuple = None):
    total_page_num = 1
    result = data
    if pagination:
        page_size, page_num = pagination
        paginator = Paginator(data, page_size)
        try:
            res = paginator.page(page_num)
        except PageNotAnInteger:
            res = paginator.page(2)
        except EmptyPage:
            res = paginator.page(paginator.num_pages)
        result = res.object_list
        total_page_num = res.paginator.num_pages
    
    return (result, total_page_num)

def get_response_data(request, queryset):
    if 'page_size' in request.query_params and request.query_params['page_size'] and \
                'page_num' in request.query_params and request.query_params['page_num']:
        page_size = request.query_params['page_size']
        page_num = request.query_params['page_num']
        objects, total_page_num = get_data(queryset,
                                             pagination=(page_size,
                                                         page_num))
    else:
        objects, total_page_num = get_data(queryset)

    return objects, total_page_num

def get_user_roles(user):
    roles = []
    if isinstance(user, User):
        roles = [r.role.title for r in UserRole.objects.filter(user=user)]
    return roles

def check_duplicate_request(user, requested_role, organization):
    return Request.objects.filter(
        user=user,
        requested_role=requested_role,
        organization=organization,
        status=Request.Status.PENDING
    ).exists()

def update_role_request(request):
    user = request.user
    user_roles = get_user_roles(user)
    role = request.requested_role
    organization = request.organization
    
    if role in user_roles:
        raise ProjectException(
            message = f'user already has role {role}',
        )
    if 'org_employee' in user_roles and (not user.organization == organization):
        raise ProjectException(
            message = 'user organization is not matched with requested organization',
        )

    user.organization=organization
    user.save()
    try:
        role_object = Role.objects.get(title=role)
    except Role.DoesNotExist:
        raise ProjectException(
            803,
            'not found',
            f'This role {role} does not exist.',
            status.HTTP_404_NOT_FOUND
        )
    instance = UserRole.objects.create(user=user, role=role_object)
    return instance