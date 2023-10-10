from django.db import transaction
from django.db.models import F, CharField, Value as V
from django.db.models.functions import Concat

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


from user.models import User
from user.serializers import *
from utilities.functions import *
from utilities.decorators import *
from utilities.authentication import sign_in, sign_out
from utilities.exceptions import ProjectException



class DefualtViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == "register":
            return UserRegisterSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "logout":
            return UserNoneSerializer
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
                'username': user.username,
            }
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

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ([AllowAny])
    
    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        role_list = get_user_roles(user)
        queryset = queryset.annotate(
            name=Concat(
                F("first_name"), V(" "), F("last_name"), 
                output_field=CharField()
            )
        )
        if not user.pk:
            return queryset.filter(pk=-1)
        elif user.is_superuser:
            queryset = queryset
        elif 'client' in role_list:
            queryset = queryset.filter(pk=user.pk)
        else:
            queryset = queryset.filter(is_superuser=False)
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['me', 'retrieve', 'list']:
            return User
        elif self.action == 'status':
            return UserStatusSerializer
        elif self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'recycle':
            return UserNoneSerializer
        elif self.action == 'add_role':
            return UserRoleSerializer
        else:
            return self.serializer_class
    
    def filter_queryset(self, queryset, status=None):
        filters = {}
        
        if 'search' in self.request.query_params:
            filters['name__icontains'] = self.request.query_params['search']
        if status:
            filters['status'] = status
        elif 'status' in self.request.query_params and self.request.query_params['status']:
            status = get_dict_data(self.request.GET).get('status', None)
            if not isinstance(status, list):
                status = [status,]
            filters['status__in'] = status
        else:
            filters['status__in'] = [User.Status.PUBLISH, User.Status.UNPUBLISH]
            
        return queryset.filter(**filters).distinct()
    
    def get_object(self, pk=None):
        if not pk:
            raise ProjectException(
                803,
                'not found',
                'Set the primary key.',
                status.HTTP_400_BAD_REQUEST
            )
        try:
            return self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            raise ProjectException(
                803,
                'not found',
                'This primary key not found.',
                status.HTTP_404_NOT_FOUND
            )
    
    # def get_permissions(self):
        if self.action in ['resend',]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    @action(methods=['get'], detail=False)
    def me(self, request):
        user = request.user
        if isinstance(user, User):
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    @execute_with_permission('user', 'create')
    def create(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data, context={'request': request})
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
    
    @execute_with_permission('user', 'read')
    def retrieve(self, request, pk=None):
        obj = self.get_object(pk)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @execute_with_permission('user', 'update')
    @transaction.atomic
    def partial_update(self, request, pk=None):
        user = self.get_object(pk)
        data = get_dict_data(request.data)
        serializer = self.get_serializer(user, data=data,
                                        partial=True, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            serializer = UserInfoSerializer(instance=obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('user', 'delete')
    def destroy(self, request, pk=None):
        obj = self.get_object(pk)
        user = request.user
        if user.pk == obj.pk:
            raise ProjectException(
                821,
                'Forbidden',
                'You do not have permission to perform this action.',
                status.HTTP_403_FORBIDDEN
            )
        if obj.status == User.Status.TRASH:
            obj.delete()
        else:
            obj.status = User.Status.TRASH
            obj.is_active = False
            obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @execute_with_permission('user', 'status')
    @action(methods=['post'], detail=False)
    @transaction.atomic
    def status(self, request):
        user = request.user
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            users = serializer.validated_data['ids']
            new_status = serializer.validated_data['status']
            if users and (status is not None):
                for obj in users:
                    if obj.pk == user.pk:
                        raise ProjectException(
                            821,
                            'Forbidden',
                            'You do not have permission to perform this action.',
                            status.HTTP_403_FORBIDDEN
                        )
                    obj.status = new_status
                    if new_status == User.Status.UNPUBLISH:
                        obj.is_active = False
                    elif new_status == User.Status.PUBLISH:
                        obj.is_active = True
                self.queryset.bulk_update(users, ['status', 'is_active'])
                return Response(status=status.HTTP_200_OK)
            else:
                raise ProjectException(
                    807,
                    'not found',
                    'Primary keys list is empty.',
                    status.HTTP_404_NOT_FOUND
                )
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('user', 'trash')
    @action(methods=['get'], detail=False)
    def deleted(self, request):
        queryset = self.filter_queryset(self.get_queryset(), User.Status.TRASH).order_by('id')
        if not queryset.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        queryset, total_page_num = get_response_data(request, queryset)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'list': serializer.data,
            'total_page_num': total_page_num,
            'total_row': queryset.count()
        },
        status=status.HTTP_200_OK
        )
    
    @execute_with_permission('user', 'recycle')
    @action(methods=['patch'], detail=True)
    @transaction.atomic
    def recycle(self, request, pk=None):
        obj = self.get_object(pk)
        user = request.user
        if user.pk == obj.pk:
            raise ProjectException(
                821,
                'Forbidden',
                'You do not have permission to perform this action.',
                status.HTTP_403_FORBIDDEN
            )
        if obj.status == User.Status.TRASH:
            obj.status = User.Status.PUBLISH
            obj.is_active = True
            obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'not found',
                'This primary key not found.',
                status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=["post", "delete"], url_path='role')
    def role(self, request):
        if request.method == "POST":
            return self.add_role(request)
        elif request.method == "DELETE":
            return self.delete_role(request)
    
    @execute_with_permission('userrole', 'create')
    @transaction.atomic
    def add_role(self, request):
        data = get_dict_data(request.data)
        serializer = UserRoleSerializer(data=data, partial=True)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            serializer.save()
            responce_serializer = UserInfoSerializer(instance=user)
            return Response(responce_serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('userrole', 'delete')
    @transaction.atomic
    def delete_role(self, request):
        data = get_dict_data(request.data)
        serializer = UserRoleSerializer(data=data, partial=True)
        if serializer.is_valid():
            user = serializer.validated_data.get('user', None)
            role = serializer.validated_data.get('role', None)
            print(serializer.validated_data)
            if not user or not role:
                raise ProjectException(
                    807,
                    'validation error',
                    serializer.errors,
                    status.HTTP_400_BAD_REQUEST
                )
            if user.pk == request.user.pk:
                raise ProjectException(
                    821,
                    'Forbidden',
                    'You do not have access to delete your role.',
                    status.HTTP_403_FORBIDDEN
                )
            try:
                UserRole.objects.get(user=user, role=role).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except UserRole.DoesNotExist:
                raise ProjectException(
                        847,
                        "not found",
                        "This role not found.",
                        status.HTTP_404_NOT_FOUND,
                    )
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )