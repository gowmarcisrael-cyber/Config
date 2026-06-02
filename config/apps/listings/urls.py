from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('search/',views.search,name='search'),
    path('detail/<int:id>/',views.detail,name='listing_detail'),
    path('create/',views.create_listing,name='create-listing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('dashboard/listings/<int:pk>/status/', views.listing_change_status, name='listing_change_status'),
    path('dashboard/listings/<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<int:pk>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('dashboard/listings/favorite/',views.listings_favorite,name='favorite'),
]