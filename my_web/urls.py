
from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    path('confirm-email/', views.confirm_email, name='confirm_email'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('task/create/', views.create_task, name='create_task'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('task/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:pk>/finish/', views.finish_task, name='finish_task'),
    path('task/<int:pk>/cancel/', views.cancel_task, name='cancel_task'),
    path('profile/', views.profile, name='profile'),
    path('send-announcement/', views.send_announcement, name='send_announcement'),
]
