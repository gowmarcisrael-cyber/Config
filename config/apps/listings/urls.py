from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('search/',views.search,name='search'),
    path('detail/<int:id>/',views.detail,name='listing-detail'),
    path('create/',views.create_listing,name='create-listing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('dashboard/listings/<int:pk>/status/', views.listing_change_status, name='listing_change_status'),
    path('dashboard/listings/<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<int:pk>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('dashboard/listings/favorite/',views.listings_favorite,name='favorite'),
    path('staff/', views.staff_listings, name='staff_listings'),
    path('staff/listings/<int:pk>/approve/', views.staff_approve_listing, name='staff_approve_listing'),
    path('staff/members/',views.staff_users,name='staff_users'),
    path('staff/users/', views.staff_users, name='staff_users'),
    path('staff/users/<int:pk>/toggle/', views.staff_toggle_user, name='staff_toggle_user'),
    path('staff/stats/', views.staff_stats, name='staff_stats'),
]