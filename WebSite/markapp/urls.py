from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('registration/', views.register, name='registration'),
    path('userprofile/', views.user_profile, name='userprofile'),
    path('editprofile/', views.edit_profile, name='editprofile'),
    path('tasklist/', views.task_list, name='tasklist'),
    path('taskcreate/<int:profile_group_id>',
         views.create_task,
         name='taskcreate'),
    path('api/get-group-users/<int:group_id>/',
         views.get_group_users,
         name='get_group_users'),
    path('creategroup/', views.create_group, name='creategroup'),
    #     path('groups/', views.group_view, name='groups'),
    path('groups/<int:profile_group_id>/', views.group_view, name='group'),
    path('groups/<int:group_id>/add-users/',
         views.add_user_to_group,
         name='addusertogroup'),
    path('groups/delete/', views.delete_group, name='delete_group'),
    path('tasks/delete/', views.delete_task, name='delete_task'),
    path('groups/<int:group_id>/tasks/', views.group_tasks,
         name='group_tasks'),
    path('groups/<int:group_id>/create-achievement/',
         views.create_achievement,
         name='create_achievement'),
    path('achievement-list/', views.achievement_list, name='achievement_list'),
    path('groups/<int:group_id>/bulk-assign-achievements/',
         views.bulk_assign_achievements,
         name='bulk_assign_achievements'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
