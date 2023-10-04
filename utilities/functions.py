
from datetime import datetime
import jwt
from django.conf import settings

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