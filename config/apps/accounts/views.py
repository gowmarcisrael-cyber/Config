from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
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
        avatar = request.FILES['avatar']
        if avatar:
            if request.user.avatar:
                request.user.avatar.remove()
            request.user.avatar = avatar
            request.user.save()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
    return render(request,'accounts/profile/profile.html')

def edit_profile(request):
    return render(request,'accounts/edit_profile.html')

def change_password(request):
    return render(request,'accounts/change_password.html')

def delete_account(request):
    return render(request,'accounts/delete_account.html')

