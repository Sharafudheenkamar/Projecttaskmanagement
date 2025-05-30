from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions  
from .models import Task, UserProfile, Role
from .serializers import TaskSerializer, TaskReportSerializer, UserProfileSerializer, UserSerializer
from .permissions import IsSuperAdmin, IsAdminOrSuperAdmin, IsTaskAssigneeOrAdmin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import View






from .models import UserProfile

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        # If user is already authenticated, redirect to admin panel
        if request.user.is_authenticated:
            return redirect('admin_panel')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check user role and redirect to admin panel
            if hasattr(user, 'userprofile'):
                role = user.userprofile.role.name
                if role in ['Admin', 'SuperAdmin']:
                    messages.success(request, 'Login successful')
                    return redirect('admin_panel')
                else:
                    messages.error(request, 'Access restricted to Admin and SuperAdmin roles')
                    return redirect('login')
            else:
                messages.error(request, 'User profile not found')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

# API Views
class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTaskAssigneeOrAdmin]
    
    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            self.check_object_permissions(request, task)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class TaskReportView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if task.status != 'COMPLETED':
                return Response({'error': 'Task is not completed'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TaskReportSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

# Admin Panel Views
class AdminPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_panel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return context
        
        role = user.userprofile.role.name
        context['is_superadmin'] = role == 'SuperAdmin'
        context['is_admin'] = role == 'Admin'
        
        if role == 'SuperAdmin':
            context['users'] = User.objects.all()
            context['tasks'] = Task.objects.all()
            context['roles'] = Role.objects.all()
        elif role == 'Admin':
            assigned_users = UserProfile.objects.filter(assigned_admin=user)
            user_ids = assigned_users.values_list('user_id', flat=True)
            context['users'] = User.objects.filter(id__in=user_ids)
            context['tasks'] = Task.objects.filter(assigned_to__in=user_ids)
        
        return context

class CreateUserView(LoginRequiredMixin, TemplateView):
    template_name = 'create_user.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.all()
        context['admins'] = User.objects.filter(userprofile__role__name='Admin')
        return context
    
    def post(self, request):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'SuperAdmin':
            messages.error(request, 'Unauthorized access')
            return redirect('admin_panel')
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role_id = request.POST.get('role')
        admin_id = request.POST.get('assigned_admin')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            role = Role.objects.get(id=role_id)
            assigned_admin = User.objects.get(id=admin_id) if admin_id else None
            UserProfile.objects.create(user=user, role=role, assigned_admin=assigned_admin)
            messages.success(request, 'User created successfully')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
        
        return redirect('admin_panel')
    

# Delete User View
class DeleteUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'SuperAdmin':
            messages.error(request, 'Unauthorized access')
            return redirect('admin_panel')

        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            messages.error(request, 'Cannot delete your own account')
            return redirect('admin_panel')

        try:
            user.delete()
            messages.success(request, 'User deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('admin_panel')

# Assign User to Admin View
class AssignUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'SuperAdmin':
            messages.error(request, 'Unauthorized access')
            return redirect('admin_panel')

        user = get_object_or_404(User, id=user_id)
        admin_id = request.POST.get('assigned_admin')
        try:
            user_profile = user.userprofile
            if admin_id:
                user_profile.assigned_admin = get_object_or_404(User, id=admin_id)
            else:
                user_profile.assigned_admin = None
            user_profile.save()
            messages.success(request, 'User assignment updated successfully')
        except Exception as e:
            messages.error(request, f'Error assigning user: {str(e)}')
        return redirect('admin_panel')

class DeleteTaskView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'SuperAdmin':
            messages.error(request, 'Unauthorized access')
            return redirect('admin_panel')

        task = get_object_or_404(Task, id=task_id)
        try:
            task.delete()
            messages.success(request, 'Task deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting task: {str(e)}')
        return redirect('admin_panel')


class CreateTaskView(LoginRequiredMixin, TemplateView):
    template_name = 'create_task.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.role.name == 'Admin':
            assigned_users = UserProfile.objects.filter(assigned_admin=user)
            context['users'] = User.objects.filter(id__in=assigned_users.values_list('user_id', flat=True))
        else:
            context['users'] = User.objects.all()
        return context
    
    def post(self, request):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name not in ['Admin', 'SuperAdmin']:
            messages.error(request, 'Unauthorized access')
            return redirect('admin_panel')
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        try:
            Task.objects.create(
                title=title,
                description=description,
                assigned_to=User.objects.get(id=assigned_to_id),
                due_date=timezone.datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
            )
            messages.success(request, 'Task created successfully')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')
        
        return redirect('admin_panel')
