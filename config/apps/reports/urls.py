from django.urls import path
from . import views

urlpatterns = [
    path('listings/<slug:slug>/', views.report_listing, name='report_listing'),
    path('users/<str:username>/', views.report_user, name='report_user'),
    path('<int:pk>/delete/', views.delete_report, name='delete_report'),
]