from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm


def signup_view(request):
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'staff'):
            return redirect('main:staff_dashboard')
        return redirect('main:home')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            # Redirect based on role
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'staff'):
                return redirect('main:staff_dashboard')
            return redirect('main:home')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'staff'):
            return redirect('main:staff_dashboard')
        return redirect('main:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect based on role
                if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'staff'):
                    return redirect('main:staff_dashboard')
                return redirect('main:home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
