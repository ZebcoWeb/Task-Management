import jwt
from datetime import datetime


from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import status

from user.models import Token
from user.serializers import TokenSerializer
from utilities.functions import get_player_id, generate_new_token
from utilities.exceptions import ProjectException



class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
    model = Token
    
    def authenticate(self, request):
        ret = super().authenticate(request._request)
        if ret:
            user, token = ret
            if token.key:
                object = jwt.decode(token.key, key=settings.SECRET_KEY, algorithms=settings.SECRET_ALGORITM)
                player_id = object.get('player_id')
                expires_at = object.get('expires_at')
                date_time_exp = datetime.strptime(expires_at, '%B %d %Y - %H:%M:%S')
                date_time_now = datetime.strptime(datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'), '%B %d %Y - %H:%M:%S')
                req_player_id = get_player_id(request)[0]
                if req_player_id != player_id:
                    raise ProjectException(
                        801,
                        'authentication error',
                        'The token is invalid for this system.',
                        status_code=status.HTTP_401_UNAUTHORIZED
                    )   
                elif date_time_now > date_time_exp:
                    raise ProjectException(
                        801,
                        'authentication error',
                        'The access token has expired.',
                        status_code=status.HTTP_401_UNAUTHORIZED
                    )
        return ret

def sign_in(request, data):
    chk, user, access_token, refresh_token = authenticate(request,data)
    if chk:
        login(request, user)
        return (True, user, access_token, refresh_token)
    return (False, None, None, None)

def sign_out(request):
    chk = delete_player_id(request)
    if chk:
        logout(request)
        return Response({"message": 'token burned'} , status=status.HTTP_200_OK)
    return Response({"message": 'bad request'} , status=status.HTTP_400_BAD_REQUEST)
    
def authenticate(request, data):
    player_id, remote_addr, user_agent = get_player_id(request)
    serializer = AuthTokenSerializer(data=data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        access_token = generate_new_token(
            user.id,
            user.username,
            player_id,
            settings.ACCESS_TOKEN_EXPIRE_TIME,
            'access_token'
        )
        refresh_token = generate_new_token(
            user.id,
            user.username,
            player_id,
            settings.REFRESH_TOKEN_EXPIRE_TIME,
            'refresh_token'
        )
        data = {
            'key': access_token,
            'refresh_token': refresh_token, 
            'player_id': player_id,
            'remote_addr': remote_addr,
            'user_agent': user_agent,
            'user': user.id
        }
        token = TokenSerializer(data=data)
        if token.is_valid():
            token = token.save()
            return (True, user, token.key, token.refresh_token)
    return (False, None, None, None)

def delete_player_id(request):
    player_id, remote_addr, user_agent = get_player_id(request)
    user = request.user if request.user else None
    
    if player_id and user:
        try:
            token = Token.objects.get(player_id=player_id, user=user)
            token = token.delete()
        except:
            pass
    return False