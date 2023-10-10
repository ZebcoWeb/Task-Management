from rest_framework import serializers, status
from django.db import models

from request.models import Request
from org.models import Organization
from user.models import User
from utilities.functions import *
from utilities.exceptions import ProjectException

class RequestSerializer(serializers.Serializer):
    class StatusChoices(models.TextChoices):
        PENDING = 0
        ACCEPTED = 1
        REJECTED = -1
    class RequestedRoleChoices(models.TextChoices):
        ORG_MANAGER = 'org_manager'
        ORG_EMPLOYEE = 'org_employee'
        
    class Meta:
        model = Request
        fields = ['id', 'user', 'status', 'requested_role', 'organization', 'created_at']
        read_only_fields = ['id', 'created_at', 'status', 'user']
    
    id = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(choices=StatusChoices.choices, read_only=True)
    requested_role = serializers.ChoiceField(choices=RequestedRoleChoices.choices, required=True)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(status=Organization.Status.PUBLISH), 
        error_messages={
            'does_not_exist': 'Organization does not exist.',
            'invalid': 'invalid value'
            },
        required=False,
        )
    
    def validate(self, data):
        self.user = get_user(context=self.context)
        requested_role = data.get('requested_role')
        organization = data.get('organization', None)
        role_list = get_user_roles(self.user)
        
        if requested_role in role_list:
            raise ProjectException(
                803,
                'invalid value',
                'You already have this role.',
                status.HTTP_400_BAD_REQUEST
            )
        if requested_role == self.RequestedRoleChoices.ORG_EMPLOYEE and (not organization):
            raise ProjectException(
                803,
                'invalid value',
                'Organization must be specified for ORG_EMPLOYEE role.',
                status.HTTP_400_BAD_REQUEST
            )
        else:
            data['organization'] = organization
            
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.user
        validated_data['status'] = self.StatusChoices.PENDING
        validated_data['organization'] = validated_data.get('organization')
                
        new_instance = self.Meta.model(**validated_data)
        if check_duplicate_request(self.user, new_instance.requested_role, new_instance.organization):
            raise ProjectException(
                803,
                'invalid value',
                'This request already exists.',
                status.HTTP_400_BAD_REQUEST
            )
        new_instance.save()
        return new_instance
    

class RequestStatusSerializer(serializers.Serializer):
    class StatusChoices(models.TextChoices):
        ACCEPTED = 1
        REJECTED = -1
        
    id = serializers.PrimaryKeyRelatedField(
        queryset=Request.objects.filter(status=Request.Status.PENDING),
        error_messages={
            'does_not_exist':
            "user does not exist",
            'invalid': "invalid value"
        }
    )
    status = serializers.ChoiceField(choices=StatusChoices.choices, required=True)
    
    def validate(self, data):
        status = data.get('status')
        if status not in self.StatusChoices.values:
            raise ProjectException(
                827, 
                'validation error', 
                'Status is invalid.', 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return data
    
    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.modified_by = get_user(context=self.context)
        if instance.status == self.StatusChoices.ACCEPTED:
            update_role_request(instance)
        instance.save()
        return instance

        