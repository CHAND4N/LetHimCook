from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Restaurant, Dish

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('accounts:login')

        if not (request.user.is_superuser or request.user.profile.role == 'staff'):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('main:home')

        return view_func(request, *args, **kwargs)
    return wrapper


def owner_or_superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('accounts:login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check for restaurant ownership
        restaurant_id = kwargs.get('restaurant_id')
        if restaurant_id:
            try:
                restaurant = Restaurant.objects.get(pk=restaurant_id)
                if restaurant.owner != request.user:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('main:restaurant_detail', restaurant_id=restaurant_id)
            except Restaurant.DoesNotExist:
                messages.error(request, 'Restaurant not found.')
                return redirect('main:staff_dashboard')

        # Check for dish ownership
        dish_id = kwargs.get('dish_id')
        if dish_id:
            try:
                dish = Dish.objects.get(pk=dish_id)
                if dish.restaurant.owner != request.user:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('main:restaurant_detail', restaurant_id=dish.restaurant.id)
            except Dish.DoesNotExist:
                messages.error(request, 'Dish not found.')
                return redirect('main:staff_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper
