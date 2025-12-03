from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Restaurant, Dish
from .forms import RestaurantForm, DishForm
from .decorators import staff_required, owner_or_superuser_required


def home_view(request):
    return render(request, 'home.html')


@login_required
@staff_required
def staff_dashboard(request):
    """Staff dashboard showing restaurants created by logged-in staff"""
    if request.user.is_superuser:
        restaurants = Restaurant.objects.all()
    else:
        restaurants = Restaurant.objects.filter(owner=request.user)
    
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'main/staff_dashboard.html', context)


@login_required
def restaurant_detail(request, restaurant_id):
    """Restaurant detail page showing restaurant info and dishes"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    dishes = restaurant.dishes.all()
    
    # Check if user is owner or superuser
    can_edit = request.user.is_superuser or restaurant.owner == request.user
    
    context = {
        'restaurant': restaurant,
        'dishes': dishes,
        'can_edit': can_edit,
    }
    return render(request, 'main/restaurant_detail.html', context)


@login_required
@staff_required
def create_restaurant(request):
    """Create a new restaurant (staff or superuser only)"""
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            form.save_m2m()  # Save many-to-many relationships (cuisines)
            messages.success(request, f'Restaurant "{restaurant.name}" created successfully!')
            return redirect('main:restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = RestaurantForm()
    
    context = {
        'form': form,
        'title': 'Create Restaurant',
    }
    return render(request, 'main/restaurant_form.html', context)


@login_required
@owner_or_superuser_required
def update_restaurant(request, restaurant_id):
    """Update restaurant (owner or superuser only)"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            form.save_m2m()  # Save many-to-many relationships (cuisines)
            messages.success(request, f'Restaurant "{restaurant.name}" updated successfully!')
            return redirect('main:restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = RestaurantForm(instance=restaurant)
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'title': 'Update Restaurant',
    }
    return render(request, 'main/restaurant_form.html', context)


@login_required
@owner_or_superuser_required
def delete_restaurant(request, restaurant_id):
    """Delete restaurant (owner or superuser only)"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    
    if request.method == 'POST':
        restaurant_name = restaurant.name
        restaurant.delete()
        messages.success(request, f'Restaurant "{restaurant_name}" deleted successfully!')
        return redirect('main:staff_dashboard')
    
    context = {
        'restaurant': restaurant,
    }
    return render(request, 'main/restaurant_confirm_delete.html', context)


@login_required
@owner_or_superuser_required
def add_dish(request, restaurant_id):
    """Add a dish to a restaurant (owner or superuser only)"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            dish = form.save(commit=False)
            dish.restaurant = restaurant
            dish.save()
            messages.success(request, f'Dish "{dish.name}" added successfully!')
            return redirect('main:restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = DishForm()
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'title': 'Add Dish',
    }
    return render(request, 'main/dish_form.html', context)


@login_required
@owner_or_superuser_required
def update_dish(request, dish_id):
    """Update dish (owner or superuser only)"""
    dish = get_object_or_404(Dish, pk=dish_id)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dish "{dish.name}" updated successfully!')
            return redirect('main:restaurant_detail', restaurant_id=dish.restaurant.id)
    else:
        form = DishForm(instance=dish)
    
    context = {
        'form': form,
        'dish': dish,
        'restaurant': dish.restaurant,
        'title': 'Update Dish',
    }
    return render(request, 'main/dish_form.html', context)


@login_required
@owner_or_superuser_required
def delete_dish(request, dish_id):
    """Delete dish (owner or superuser only)"""
    dish = get_object_or_404(Dish, pk=dish_id)
    restaurant_id = dish.restaurant.id
    
    if request.method == 'POST':
        dish_name = dish.name
        dish.delete()
        messages.success(request, f'Dish "{dish_name}" deleted successfully!')
        return redirect('main:restaurant_detail', restaurant_id=restaurant_id)
    
    context = {
        'dish': dish,
        'restaurant': dish.restaurant,
    }
    return render(request, 'main/dish_confirm_delete.html', context)
