from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('search/',views.search,name='search'),
    path('detail/<slug:slug>/',views.detail,name='listing_detail'),
    path('create/',views.create_listing,name='create-listing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/listings/<slug:slug>/delete/', views.listing_delete, name='listing_delete'),
    path('dashboard/listings/<slug:slug>/status/', views.listing_change_status, name='listing_change_status'),
    path('dashboard/listings/<slug:slug>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<slug:slug>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('dashboard/listings/favorite/',views.listings_favorite,name='favorite'),
    path('autocomplete/cities/', views.city_autocomplete, name='city_autocomplete'),
    path('map/', views.map_view, name='map'),
    path('ai-search/', views.ai_search, name='ai_search'),
]