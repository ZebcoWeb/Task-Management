from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction


from request.models import Request
from request.serializers import *
from utilities.functions import *
from utilities.decorators import *


class RequestViewSet(viewsets.GenericViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = ([IsAuthenticated,])
    permission_classes = ([AllowAny,])
    
    
    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        role_list = get_user_roles(user)
        
        if not user.pk:
            return queryset.none()
        elif 'admin' in role_list:
            return queryset.filter()
        elif 'org_manager' in role_list:
            return queryset.filter(organization=user.organization)
        else:
            return queryset.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'status':
            return RequestStatusSerializer
        else:
            return self.serializer_class
    
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
    
    @execute_with_permission('request', 'create')
    @transaction.atomic
    def create(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(
                801,
                'invalid value',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('request', 'update')
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def status(self, request):
        data = get_dict_data(request.data)
        pk = data.get('id', None)
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance, data=data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            serializer = RequestSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('request', 'list')
    @transaction.atomic
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)