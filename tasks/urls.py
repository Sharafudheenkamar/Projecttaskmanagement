from django.urls import path
from .views import AssignUserView, DeleteTaskView, DeleteUserView, TaskListView, TaskUpdateView, TaskReportView, AdminPanelView, CreateUserView, CreateTaskView, LoginView

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task_report'),
    path('delete-user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
    path('assign-user/<int:user_id>/', AssignUserView.as_view(), name='assign_user'),
    path('delete-task/<int:task_id>/', DeleteTaskView.as_view(), name='delete_task'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('create-user/', CreateUserView.as_view(), name='create_user'),
    path('create-task/', CreateTaskView.as_view(), name='create_task'),
    path('',LoginView.as_view(),name='login')
]
