from rest_framework import serializers
from .models import Task, UserProfile, Role
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userprofile.role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True
    )
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'assigned_to_id', 
                 'due_date', 'status', 'completion_report', 'worked_hours', 
                 'created_at', 'updated_at']
    
    def validate(self, data):
        if data.get('status') == 'COMPLETED':
            if not data.get('completion_report') or not data.get('worked_hours'):
                raise serializers.ValidationError(
                    "Completion report and worked hours are required when marking task as completed."
                )
        return data

class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'completion_report', 'worked_hours', 'assigned_to']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True
    )
    assigned_admin = UserSerializer(read_only=True)
    assigned_admin_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_admin', write_only=True, allow_null=True
    )
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'role_id', 'assigned_admin', 'assigned_admin_id']
