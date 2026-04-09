from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('signup/', views.signup, name='signup'),
    path('roadmap/<int:domain_id>/', views.roadmap_view, name='roadmap'),
    path('toggle/<int:topic_id>/', views.toggle_progress, name='toggle_progress'),
    path('dashboard/', views.dashboard, name='dashboard'),
]