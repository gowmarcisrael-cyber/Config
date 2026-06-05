import os

from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash,get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes,force_str
from django.http import HttpResponse
import bleach
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.conf import settings
import uuid
# Create your views here.
User = get_user_model()

def generate_username(email):
    base = email.split("@")[0]
    username = base
    count = 1

    while User.objects.filter(username=username).exists():
        username = f"{base}{count}"
        count += 1

    return username

def send_welcome_email(request,user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        f"/accounts/activate/{uid}/{token}/"
    )
    subject = "Bienvenue sur notre plateforme"
    html_content = render_to_string(
        "emails/welcome.html",
        {
            "user": user,
            "activation_link": activation_link,
        }
    )

    text_content = f"Activez votre compte ici : {activation_link}"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified = False
            user.username = generate_username(user.email)
            user.save()
            send_welcome_email(request,user)
            return render(request,'accounts/created.html')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is None:
        return HttpResponse(status=404)

    if user.email_verified:
        return redirect('login')

    if default_token_generator.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'accounts/activated.html')

    return HttpResponse(status=404)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Récupérer l'utilisateur par email
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if user:
                if not user.email_verified:
                    messages.error(request, 'Veuillez activer votre compte.')
                    return redirect('login')
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:
                form.add_error(None, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'avatar':
            avatar = request.FILES.get('avatar')
            if avatar:
                if request.user.avatar:
                    request.user.avatar.delete()
                request.user.avatar = avatar
                request.user.save()

        elif action == 'profile':
            username = bleach.clean(request.POST.get('username', ''), tags=[], strip=True)
            
            # Vérifier si le username est déjà pris
            if username and username != request.user.username:
                if get_user_model().objects.filter(username=username).exclude(pk=request.user.pk).exists():
                    messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                    return redirect('profile')
            
            # Pareil pour l'email
            email = bleach.clean(request.POST.get('email', ''), tags=[], strip=True)
            if email and email != request.user.email:
                if get_user_model().objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    messages.error(request, "Cet email est déjà utilisé.")
                    return redirect('profile')

            first_name = bleach.clean(request.POST.get('first_name', ''), tags=[], strip=True)
            last_name = bleach.clean(request.POST.get('last_name', ''), tags=[], strip=True)

            request.user.first_name = first_name
            request.user.last_name = last_name
            if username:
                request.user.username = username
            if email:
                request.user.email = email
            request.user.save()
            messages.success(request, 'Profil mis à jour.')

        elif action == 'password':
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if old_password and new_password1 and new_password1 == new_password2:
                if request.user.check_password(old_password):
                    request.user.set_password(new_password1)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Mot de passe mis à jour.')
                else:
                    messages.error(request, 'Mot de passe actuel incorrect.')

        return redirect('profile')

    return render(request, 'accounts/profile/profile.html', {'user': request.user})


@login_required
def delete_account(request):
    send_delete_confirmation_email(request, request.user)
    return render(request, 'accounts/delete_account.html')

@login_required
def delete_confirm(request):
    return render(request, 'accounts/partials/delete_confirm.html')

@login_required
def delete_cancel(request):
    return render(request, 'accounts/partials/delete_btn.html')

@login_required
@require_POST
def delete_account(request):
    send_delete_confirmation_email(request, request.user)
    return render(request, 'accounts/partials/delete_email_sent.html')


def send_delete_confirmation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    delete_link = request.build_absolute_uri(
        f"/accounts/delete/{uid}/{token}/"
    )
    subject = "Confirmer la suppression de votre compte — HAVEN"
    html_content = render_to_string(
        "emails/account_delete_confirmation.html",
        {
            "user": user,
            "delete_link": delete_link,
        }
    )
    text_content = f"Confirmer la suppression : {delete_link}"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

def delete_account_confirm(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is None:
        return HttpResponse(status=404)

    if default_token_generator.check_token(user, token):
        logout(request)
        if user.avatar:
            user.avatar.delete(save=False)
        user.delete()
        messages.success(request, 'Votre compte a été supprimé avec succès.')
        return redirect('home')

    return HttpResponse(status=404)