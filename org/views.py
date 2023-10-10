from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import F, CharField, Value as V
from django.db.models.functions import Concat
from django.db import transaction

from org.models import Organization
from org.serializers import *
from utilities.functions import *
from utilities.decorators import *
from utilities.exceptions import ProjectException


class OrganizationViewSet(viewsets.GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = ([AllowAny,])
    # permission_classes = ([IsAuthenticated,])
    
    def get_serializer_class(self):
        if self.action in ['join_org', 'left_org']:
            return OrganizationUserSerializer
        else:
            return self.serializer_class
    
    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        role_list = get_user_roles(user)
        queryset = queryset.annotate(
            context=Concat(
                F("title"), V(" "), F("description"), 
                output_field=CharField()
            )
        )
        if not user.pk:
            return queryset.none()
        elif 'admin' in role_list:
            return queryset
        elif 'org_manager' in role_list:
            queryset.filter(functor__organization=user.organization).distinct()
        elif 'org_employee' in role_list:
            queryset.filter(created_by=user).distinct()
        else:
            # return queryset.none()
            return queryset.all()
    
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
    
    @execute_with_permission('org', 'create')
    @transaction.atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('org', 'read')
    def retrieve(self, request, pk=None):
        obj = self.get_object(pk)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @execute_with_permission('org', 'update')
    @transaction.atomic
    def partial_update(self, request, pk=None):
        obj = self.get_object(pk)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('org', 'trash')
    def destroy(self, request, pk=None):
        obj = self.get_object(pk)
        if obj.status == Organization.Status.TRASH:
            obj.delete()
        else:
            obj.status = Organization.Status.TRASH
            obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @execute_with_permission('org', 'recycle')
    @action(methods=['patch'], detail=False)
    @transaction.atomic
    def recycle(self, request, pk=None):
        obj = self.get_object(pk)
        if obj.status == User.Status.TRASH:
            obj.status = User.Status.PUBLISH
            obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'not found',
                'This primary key not found.',
                status.HTTP_404_NOT_FOUND
            )
    
    @execute_with_permission('orguser', 'create')
    @action(methods=['post'], detail=False, url_path='join')
    @transaction.atomic
    def join_org(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user_obj = User.objects.get(pk=user.id)
            if user_obj.organization:
                raise ProjectException(
                    803,
                    'not found',
                    'This user already has an organization.',
                    status.HTTP_400_BAD_REQUEST
                )
            organization = serializer.validated_data.get('organization')
            user.organization = organization
            try:
                role = Role.objects.get(title='org_employee')
            except Role.DoesNotExist:
                raise ProjectException(
                    803,
                    'not found',
                    'This role not found.',
                    status.HTTP_404_NOT_FOUND
                )
            UserRole.objects.create(
                user=user,
                role=role,
            )
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('orguser', 'delete')
    @action(methods=['post'], detail=False, url_path='left')
    @transaction.atomic
    def left_org(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user_obj = User.objects.get(pk=user.id)
            if not user_obj.organization:
                raise ProjectException(
                    803,
                    'not found',
                    'This user does not have an organization.',
                    status.HTTP_400_BAD_REQUEST
                )
            user_role = UserRole.objects.get(user=user, role__title='org_employee')
            if not user_role:
                raise ProjectException(
                    803,
                    'not found',
                    'User role must be org_employee.',
                    status.HTTP_400_BAD_REQUEST
                )
            user.organization = None
            user.save()
            user_role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )