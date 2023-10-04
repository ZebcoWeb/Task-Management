
import jwt
from datetime import datetime
from rest_framework import serializers
from rest_framework import status

from django.conf import settings

from user.models import User, Token
from utilities.exceptions import ProjectException
from utilities.functions import get_user, get_player_id, generate_new_token


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'id']
    
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=130, required=True, write_only=True)
    
    def validate(self, data):
        self.user  = get_user(context=self.context)
        if not self.user.pk:
            self.user = None
        password  = data.get('password', None)
        username  = data.get('username', None)

        if User.objects.filter(username=username).exists():
            raise ProjectException(
                809, 
                'validation error', 
                'There is a user with this email in this system.', 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if password:
            if len(password) < 8:
                raise ProjectException(
                        812, 
                        'validation error', 
                        "password cannot les than 8 digit",
                        status.HTTP_400_BAD_REQUEST
                    )
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.user
        validated_data['modified_by'] = self.user
        new_instance = self.Meta.model(**validated_data)
        new_instance.first_name = validated_data.get('first_name', None)
        new_instance.last_name = validated_data.get('last_name', None)
        new_instance.username = validated_data.get('username')
        new_instance.set_password(validated_data.get('password'))
        
        new_instance.save()
        return new_instance
    
class UserInfoSerializer(serializers.Serializer):

    id          = serializers.IntegerField(read_only=True)
    first_name  = serializers.CharField(read_only=True)
    last_name   = serializers.CharField(read_only=True)
    name        = serializers.SerializerMethodField(read_only=True)
    username    = serializers.CharField(read_only=True)
    is_active   = serializers.BooleanField(read_only=True)
    created_at     = serializers.DateTimeField(read_only=True)
    
    def get_name(self, obj):
        name = "".join([obj.first_name, ' ', obj.last_name])
        return name
    
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key','refresh_token', 'user', 'remote_addr', 'user_agent', 'player_id')

    key  = serializers.CharField(max_length=None)
    refresh_token = serializers.CharField(max_length=None)
    remote_addr = serializers.CharField(max_length=None)
    player_id = serializers.CharField(max_length=None)
    user_agent = serializers.CharField(max_length=None)
    user = serializers.PrimaryKeyRelatedField(many=False,
                                              queryset=User.objects.all(),
                                              error_messages={
                                                  'does_not_exist':
                                                  "user does not exist",
                                                  'invalid': "invalid value"
                                              })

    
    def create(self, validated_data):
        player_id = validated_data['player_id']
        remote_addr = validated_data['remote_addr']
        user_agent = validated_data['user_agent']
        user = validated_data['user']
        user_id = user.id
        if player_id:
            try:
                object = Token.objects.get(player_id=player_id)
                object.delete()
            except Token.DoesNotExist:
                pass
        new_instance = self.Meta.model(**validated_data)
        new_instance.save()
        return new_instance

class UserLoginSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, read_only=True)
    last_name = serializers.CharField(max_length=150, read_only=True)
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=130, required=True)
    
    is_active = serializers.BooleanField(read_only=True)
    
    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise ProjectException(
                809, 
                'validation error', 
                'There is no user with this username.', 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if user.login_error == settings.DEACTIVE_COUNT:
            raise ProjectException(
                        804,
                        "authentication error",
                        "You have been disabled by the system for security reasons.",
                        status.HTTP_401_UNAUTHORIZED,
                    )
            
        if not user.check_password(data['password']):
            user.login_error += 1
            if user.login_error == settings.DEACTIVE_COUNT:
                if user.is_active:
                    user.is_active = False
                    user.save()
                raise ProjectException(
                        804,
                        "authentication error",
                        "You have been disabled by the system for security reasons.",
                        status.HTTP_401_UNAUTHORIZED,
                    )
            user.save()
            raise ProjectException(
                804, 
                'authentication error', 
                'Authentication error', 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        elif not user.is_active:
            raise ProjectException(
                804, 
                'authentication error', 
                'You have been disabled by the system.', 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        return data

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=130, required=True)
    new_password = serializers.CharField(max_length=130, required=True)
    
    def validate(self, data):
        user = get_user(context=self.context)
        current_password = data.get('current_password', None)
        new_password = data.get('new_password', None)
        
        if not len(new_password) < 8:
            raise ProjectException(
                812, 
                'validation error', 
                "password cannot les than 8 digit",
                status.HTTP_400_BAD_REQUEST
            )
        if new_password == current_password:
            raise ProjectException(
                812, 
                'validation error', 
                "new password cannot be the same as the current password",
                status.HTTP_400_BAD_REQUEST
            )
        
        return data
    
    def update(self, instance, validated_data):
        user = get_user(context=self.context)
        user.set_password(validated_data['new_password'])
        user.save()
        return user
    
class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=None, required=True)
    access_token = serializers.CharField(read_only=True)
    
    def validate(self, data):
        request = self.context.get('request')
        refresh_token = data.get('refresh_token', None)
        
        try:
            refresh_token_decode = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=settings.SECRET_ALGORITM)
            if refresh_token_decode['grant_type'] != 'refresh_token':
                raise ProjectException(
                    801,
                    'authentication error',
                    'The refresh token is invalid.',
                    status.HTTP_401_UNAUTHORIZED
                )
            player_id = refresh_token_decode['player_id']
            user_id     = refresh_token_decode['user_id']
            username   = refresh_token_decode['username']
            unlimited   = refresh_token_decode['unlimited']
            expires_at  = refresh_token_decode['expires_at']
            date_time_exp = datetime.strptime(expires_at, '%B %d %Y - %H:%M:%S')
            date_time_now = datetime.strptime(datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'), '%B %d %Y - %H:%M:%S')
            
            
            if player_id != get_player_id(request)[0]:
                raise ProjectException(
                    801,
                    'authentication error',
                    'The token is invalid for this system.',
                    status.HTTP_401_UNAUTHORIZED
                )
            elif date_time_exp < date_time_now:
                raise ProjectException(
                    801,
                    'authentication error',
                    'The token has expired.',
                    status.HTTP_401_UNAUTHORIZED
                )
            try:
                self.instance = Token.objects.get(player_id=player_id, refresh_token=refresh_token)
                data['key'] = generate_new_token(user_id, username, player_id, unlimited, 'access_token')
                data['refresh_token'] = generate_new_token(user_id, username, player_id, unlimited, 'refresh_token')
                
            except:
                pass
        except Exception as e:
            raise ProjectException(
                801,
                'authentication error',
                'The refresh token is invalid.',
                status.HTTP_401_UNAUTHORIZED
            )
        
        return data
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        instance.access_token = instance.key
        return instance
                
class NoneSerializer(serializers.Serializer):
    pass

# Sample for responses schema:
class SampleResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=None, required=False)
    code = serializers.IntegerField(required=False)
    message = serializers.CharField(max_length=None, required=False)
    detail = serializers.CharField(max_length=None, required=False)
    # data    = serializers.DictField(child=serializers.CharField(), allow_empty=True)
    
class SampleSomeResponseSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)
    deletes = serializers.ListField(child = serializers.CharField(max_length=None), required=False)
    virtual_delete = serializers.ListField(child = serializers.CharField(max_length=None), required=False)
    # data    = serializers.DictField(child=serializers.CharField(), allow_empty=True)
    
class SampleSomeVirResponseSerializer(serializers.Serializer):
    virtual_delete = serializers.ListField(child = serializers.CharField(max_length=None), required=False)
    
class SampleForgetPasswordResponseSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)