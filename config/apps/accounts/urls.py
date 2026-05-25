from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile,name='profile'),
    path('profile/edit/',views.edit_profile,name='edit-profile'),
    path('profile/change-password/',views.change_password,name='change-password'),
    path('profile/delete/',views.delete_account,name='delete-account'),
]