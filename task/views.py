from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import F, CharField, Value as V
from django.db.models.functions import Concat


from task.models import *
from task.serializers import *
from utilities.functions import *
from utilities.decorators import *
from utilities.exceptions import ProjectException


class TaskViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = ([IsAuthenticated,])

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
            return queryset.none()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'trash']:
            return TaskSerializer
        elif self.action == 'partial_update':
            return TaskUpdateSerializer
        elif self.action in ['recycle', 'done']:
            return TaskNoneSerializer
        else:
            return TaskSerializer
    
    def filter_queryset(self, queryset):
        filters = {}
        
        if 'search' in self.request.query_params:
            filters['context__icontains'] = self.request.query_params['search']
        if status:
            filters['status'] = status
        elif 'status' in self.request.query_params and self.request.query_params['status']:
            status = get_dict_data(self.request.GET).get('status', None)
            if not isinstance(status, list):
                status = [status,]
            filters['status__in'] = status
        else:
            filters['status__in'] = [User.Status.PUBLISH, User.Status.UNPUBLISH]
    
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

    @execute_with_permission('task', 'create')
    @transaction.atomic
    def create(self, request):
        data = get_dict_data(request.data)
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.request = request
        if serializer.is_valid():
            instances = serializer.save()
            instances, total_page_num = get_response_data(request, instances)
            serializer = TaskInfoSerializer(instances, many=True)
        
            return Response({
                'list': serializer.data,
                'total_page_num': total_page_num,
                'total_row': len(instances)
            },
            status=status.HTTP_201_CREATED
            )
        else:
            raise ProjectException(
                801,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('task', 'read')
    def retrieve(self, request, pk=None):
        obj = self.get_object(pk)
        serializer = TaskInfoSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @execute_with_permission('task', 'delete')
    def destroy(self, request, pk=None):
        obj = self.get_object(pk)
        if obj.status == User.Status.TRASH:
            obj.delete()
        else:
            obj.status = User.Status.TRASH
            obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @execute_with_permission('task', 'update')
    @transaction.atomic
    @action(methods=['patch'], detail=True)
    def done(self, request, pk=None):
        obj = self.get_object(pk)
        user = request.user
        if obj.functor.pk != user.pk:
            raise ProjectException(
                807,
                'Forbidden',
                'You do not have permission to perform this action.',
                status.HTTP_403_FORBIDDEN
            )
        if not obj.finished_at:
            obj.finished_at = datetime.utcnow()
            obj.status = Task.Status.UNPUBLISH
            obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'finished task',
                'This task is finished before.',
                status.HTTP_404_NOT_FOUND
            )
    
    @execute_with_permission('task', 'update')
    @transaction.atomic
    def partial_update(self, request, pk=None):
        obj = self.get_object(pk)
        data = get_dict_data(request.data)
        serializer = self.get_serializer(obj, data=data, 
                                         context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer = TaskInfoSerializer(instance=obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ProjectException(
                807,
                'validation error',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
    
    @execute_with_permission('task', 'recycle')
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