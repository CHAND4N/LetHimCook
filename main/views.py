from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Restaurant, Dish, Cuisine
from .forms import RestaurantForm, DishForm
from .decorators import staff_required, owner_or_superuser_required
from django.contrib.auth.decorators import user_passes_test


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

            # save selected cuisines
            form.save_m2m()

            # handle new cuisines (comma-separated)
            new_cuisines = form.cleaned_data.get('new_cuisines')
            if new_cuisines:
                names = [c.strip() for c in new_cuisines.split(',') if c.strip()]
                for name in names:
                    normalized = name.capitalize()
                    cuisine_obj, created = Cuisine.objects.get_or_create(
                        name__iexact=normalized,
                        defaults={'name': normalized}
                    )
                    restaurant.cuisines.add(cuisine_obj)

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
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.save()
            
            form.save_m2m()  # save selected existing cuisines

            # Handle new cuisines
            new_cuisines_str = form.cleaned_data.get('new_cuisines', '')
            if new_cuisines_str:
                new_cuisine_names = [name.strip() for name in new_cuisines_str.split(',') if name.strip()]
                for cname in new_cuisine_names:
                    cuisine_obj, created = Cuisine.objects.get_or_create(name=cname)
                    restaurant.cuisines.add(cuisine_obj)

            messages.success(request, f'Restaurant "{restaurant.name}" updated successfully!')
            return redirect('main:restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'main/restaurant_form.html', {
        'form': form,
        'restaurant': restaurant,
        'title': 'Update Restaurant',
    })



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


def dish_detail(request, dish_id):
    """Dish detail page showing dish info and other dishes from same restaurant"""
    dish = get_object_or_404(Dish, pk=dish_id)
    
    # Get other dishes from the same restaurant, excluding current dish
    other_dishes = Dish.objects.filter(restaurant=dish.restaurant).exclude(pk=dish.id)[:6]
    
    # Handle add to cart (placeholder - implement cart logic as needed)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        # TODO: Add cart logic here
        messages.success(request, f'Added {quantity} x {dish.name} to cart!')
        return redirect('main:dish_detail', dish_id=dish.id)
    
    context = {
        'dish': dish,
        'other_dishes': other_dishes,
    }
    return render(request, 'main/dish_detail.html', context)

def explore(request):
    # Featured restaurants and dishes (use BooleanField 'is_featured')
    featured_restaurants = Restaurant.objects.filter(featured=True)[:10]
    featured_dishes = Dish.objects.filter(featured=True)[:10]
    
    # All dishes from all restaurants
    all_dishes = Dish.objects.all()

    context = {
        'featured_restaurants': featured_restaurants,
        'featured_dishes': featured_dishes,
        'all_dishes': all_dishes,
    }
    return render(request, 'main/explore.html', context)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def all_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'main/admin_restaurants.html', {'restaurants': restaurants})