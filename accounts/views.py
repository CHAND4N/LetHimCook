from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm, ProfileEditForm
from .models import Profile
from main.models import Order


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


from django.contrib.auth.models import User

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'staff'):
            return redirect('main:staff_dashboard')
        return redirect('main:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # ---- Allow login with username OR email ----
            if '@' in username_or_email:
                # treat it as email
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = None
            else:
                # treat it as normal username
                username = username_or_email
            # --------------------------------------------

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
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
    """Profile page with editing and order history"""
    user = request.user
    
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Get user's order history with related items
    orders = Order.objects.filter(user=user).prefetch_related('items__dish').order_by('-created_at')
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=profile, user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)
