from rest_framework import serializers
from rest_framework import status

from task.models import Task
from user.models import User
from utilities.functions import *
from utilities.exceptions import ProjectException


class TaskInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'functor', 'deadline', 'finished_at', 'created_at', 'created_by', 'modified_by']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'functors', 'deadline', 'finished_at', 'created_at']
        read_only_fields = ['id', 'finished_at', 'created_at']
    
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    deadline = serializers.DateTimeField()
    functors = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        error_messages={
            'does_not_exist': 'User does not exist.',
            'invalid': 'invalid value'
            },
        required=True,
        many=True
        )
    
    def validate(self, data):
        self.user = get_user(context=self.context)
        if not self.user.pk:
            self.user = None
        
        roles = get_user_roles(self.user)
        if 'org_employee' in roles:
            data['functors'] = [self.user,]
        
        deadline = data.get('deadline')
        created_at = data.get('created_at')
        
        if deadline and created_at and deadline < created_at:
            raise ProjectException(
                803,
                'invalid value',
                'Deadline must be greater than created_at.',
                status.HTTP_400_BAD_REQUEST
            )
        return data
    
    def create(self, validated_data):
        instances = []
        validated_data['created_by'] = self.user
        validated_data['modified_by'] = self.user
        functors = validated_data.pop('functors', [])
        new_instance = self.Meta.model(**validated_data)
        if not functors:
            functors.append(self.user)
        new_instance.title = validated_data.get('title')
        new_instance.description = validated_data.get('description')
        new_instance.status = Task.Status.PUBLISH
        for functor in functors:
            new_instance.functor = functor
            instances.append(new_instance)
        self.Meta.model.objects.bulk_create(instances)
        return instances

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['functor', 'deadline']
    
    functor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        error_messages={
            'does_not_exist': 'User does not exist.',
            'invalid': 'invalid value'
            },
        )
    deadline = serializers.DateTimeField()
    
    def validate(self, data):
        self.user = get_user(context=self.context)
        if not self.user.pk:
            self.user = None
        deadline = data.get('deadline', None)
        
        created_at = self.instance.created_at
        if deadline and deadline < created_at:
            raise ProjectException(
                803,
                'invalid value',
                'Deadline must be greater than created_at.',
                status.HTTP_400_BAD_REQUEST
            )
        return data
    
    def update(self, instance, validated_data):
        validated_data['modified_by'] = self.user
        for key, value in validated_data.items():
            if value:
                setattr(instance, key, value)
        instance.save()
        return instance
    

class TaskNoneSerializer(serializers.Serializer):
    pass
        