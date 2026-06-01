from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash,get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
import bleach
# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:
                form.add_error(None, 'Identifiants incorrects.')
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

def edit_profile(request):
    return render(request,'accounts/edit_profile.html')

def change_password(request):
    return render(request,'accounts/change_password.html')

def delete_account(request):
    return render(request,'accounts/delete_account.html')

