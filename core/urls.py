from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/explore/', views.project_explore, name='project_explore'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/apply/', views.apply_to_project, name='apply_to_project'),
    path('projects/<int:pk>/applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:pk>/decision/', views.application_decision, name='application_decision'),
    path('projects/<int:pk>/tasks/', views.task_board, name='task_board'),
    path('projects/<int:pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:pk>/comment/', views.add_comment, name='add_comment'),
]
