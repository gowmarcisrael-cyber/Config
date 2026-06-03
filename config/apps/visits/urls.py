from django.urls import path
from . import views

urlpatterns = [
    path('listings/<slug:slug>/visit/', views.request_visit, name='request_visit'),
    path('dashboard/visits/sent/', views.visits_sent, name='visits_sent'),
    path('dashboard/visits/received/', views.visits_received, name='visits_received'),
    path('dashboard/visits/<int:pk>/status/', views.update_visit_status, name='update_visit_status'),
    path('dashboard/visits/<int:pk>/cancel/', views.cancel_visit, name='cancel_visit'),
]