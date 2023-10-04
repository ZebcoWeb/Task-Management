from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg import openapi


from user.models import User
from user.serializers import *
from utilities.functions import get_dict_data
from utilities.authentication import sign_in, sign_out
from utilities.exceptions import ProjectException



class DefualtAPIView(viewsets.GenericViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == "register":
            return UserRegisterSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "logout":
            return NoneSerializer
        elif self.action == "changepassword":
            return ChangePasswordSerializer
        elif self.action == "refresh_token":
            return RefreshTokenSerializer
    
    def get_permissions(self):
        if self.action in ['register', 'login', 'refresh_token','reset_password','reset', 'logout']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    @action(methods=['post'], detail=False)
    @transaction.atomic
    def register(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data)
        serializer.request = request
        if serializer.is_valid():
            obj = serializer.save()
            serializer = UserInfoSerializer(instance=obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            chk, user, access_token, refresh_token = sign_in(request, data=data)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
        if chk:
            user.save()
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
            for attr, value in self.get_serializer(user).data.items():
                data[attr] = value
            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(key='access_token', value=access_token)
        else:
            raise ProjectException(
                801,
                'authentication error',
                'The access token has expired.',
                status.HTTP_401_UNAUTHORIZED
            )
        
        return response
    
    @action(methods=['post'], detail=False)
    def logout(self, request):
        if request.user:
            sign_out(request)
            return Response({"message": 'token burned'} , status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                801,
                'not login before',
                'User has not logged in before.',
                status.HTTP_401_UNAUTHORIZED
            )
            
    @action(methods=['post'], detail=False)
    def changepassword(self, request):
        user = request.user
        serializer = self.get_serializer(context={'request': request}, data=request.data)
        
        if serializer.is_valid():
            
            if not user.check_password(serializer.validated_data['current_password']):
                raise ProjectException(
                    801,
                    'authentication error',
                    'The current password is incorrect.',
                    status.HTTP_401_UNAUTHORIZED
                )
            user = serializer.update(user, serializer.validated_data)
            return Response({"message": 'password changed'} , status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @action(methods=['post'], detail=False)
    def refresh_token(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(context={'request': request}, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )