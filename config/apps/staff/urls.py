from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_listings, name='staff_listings'),
    path('listings/<slug:slug>/approve/', views.staff_approve_listing, name='staff_approve_listing'),
    path('members/',views.staff_users,name='staff_users'),
    path('users/', views.staff_users, name='staff_users'),
    path('users/<int:pk>/toggle/', views.staff_toggle_user, name='staff_toggle_user'),
    path('stats/', views.staff_stats, name='staff_stats'),
    path('reports/', views.staff_reports, name='staff_reports'),
    path('reports/<int:pk>/resolve/', views.resolve_report, name='resolve_report'),
    path('messages/',views.staff_message,name='staff_message'),
    path('messages/toggle-read/<int:pk>',views.toggle_message_read,name='read-msg')
]