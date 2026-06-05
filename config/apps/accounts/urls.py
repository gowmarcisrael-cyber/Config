from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/',views.register,name='register'),
    path('activate/<uid>/<token>/', views.activate, name='activate'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile,name='profile'),
    path('profile/delete/',views.delete_account,name='delete-account'),
    path('delete/confirm/', views.delete_confirm, name='delete_confirm'),
    path('delete/cancel/', views.delete_cancel, name='delete_cancel'),
    path('delete/', views.delete_account, name='delete_account'),
    path('delete/<uid>/<token>/', views.delete_account_confirm, name='delete_account_confirm'),
]

urlpatterns += [
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='accounts/password_reset.html',
         email_template_name='emails/password_reset_txt.html',
         html_email_template_name='emails/password_reset.html',
         subject_template_name='emails/password_reset_subject.txt',
         success_url='/accounts/password-reset/done/'
     ), 
     name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/'
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]