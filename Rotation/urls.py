from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main'),
    path('next/', views.next_tech, name='next_tech'),
    path('previous/', views.previous_tech, name='previous_tech'),
    path('techs/', views.tech_list, name='tech_list'),
    path('techs/create/', views.tech_create, name='tech_create'),
    path('techs/<int:pk>/update/', views.tech_update, name='tech_update'),
    path('techs/<int:pk>/delete/', views.tech_delete, name='tech_delete'),
    path('settings/', views.settings_view, name='settings'),
]
