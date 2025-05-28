from django.urls import path
from .views import TaskListView, TaskUpdateView, TaskReportView, AdminPanelView, CreateUserView, CreateTaskView

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task_report'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('create-user/', CreateUserView.as_view(), name='create_user'),
    path('create-task/', CreateTaskView.as_view(), name='create_task'),
]
