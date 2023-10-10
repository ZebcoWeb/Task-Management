from rest_framework import serializers
from rest_framework import status

from org.models import Organization
from utilities.functions import *
from utilities.exceptions import ProjectException


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']
        
        id = serializers.IntegerField(read_only=True)
        title = serializers.CharField(max_length=255, required=True)
        
    def validate(self, data):
        title = data.get('title', None)
        if Organization.objects.filter(title=title).exists():
            raise ProjectException(
                801,
                'validation error',
                'This title already exists.',
                status.HTTP_400_BAD_REQUEST
            )
        return data
        
    def create(self, validated_data):
        title = validated_data.get('title', None)
        if Organization.objects.filter(title=title).exists():
            raise ProjectException(
                801,
                'validation error',
                'This title already exists.',
                status.HTTP_400_BAD_REQUEST
            )
        new_instance = self.Meta.model(**validated_data)
        new_instance.status = Organization.status.PUBLISH
        new_instance.save()
        return new_instance
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value:
                setattr(instance, attr, value)
        instance.save()
        return instance

class OrganizationUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        error_messages={
            'does_not_exist':
            "This user does not exist.",
            'invalid': "invalid value"
        }
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        error_messages={
            'does_not_exist':
            "This organization does not exist.",
            'invalid': "invalid value"
        }
    )
    
    def validate(self, data):
        return data