from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Restaurant, Dish, Cuisine, Cart, CartItem, Order, OrderItem, Review
from .forms import RestaurantForm, DishForm
from .decorators import staff_required, owner_or_superuser_required
from django.contrib.auth.decorators import user_passes_test
import json

# Stripe import - handle case where package is not installed
try:
    import stripe
except ImportError:
    stripe = None


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


@login_required
def add_to_cart(request, dish_id):
    """Add a dish to cart or increase quantity if already exists"""
    dish = get_object_or_404(Dish, pk=dish_id)
    
    # Get or create cart for user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get or create cart item
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        dish=dish,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        # Item already exists, increase quantity
        quantity = int(request.POST.get('quantity', 1))
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Updated quantity: {cart_item.quantity} x {dish.name} in cart!')
    else:
        # New item added
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 1:
            cart_item.quantity = quantity
            cart_item.save()
        messages.success(request, f'Added {cart_item.quantity} x {dish.name} to cart!')
    
    # Redirect based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({'success': True, 'message': f'Added {cart_item.quantity} x {dish.name} to cart!'})
    
    return redirect('main:cart_page')


@login_required
def cart_page(request):
    """Display cart page with all items"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('dish', 'dish__restaurant')
    total = cart.get_total()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'main/cart.html', context)


@login_required
def increment_item(request, item_id):
    """Increment quantity of a cart item"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'subtotal': float(cart_item.get_subtotal()),
            'total': float(cart_item.cart.get_total())
        })
    
    messages.success(request, f'Updated quantity: {cart_item.quantity} x {cart_item.dish.name}')
    return redirect('main:cart_page')


@login_required
def decrement_item(request, item_id):
    """Decrement quantity of a cart item, remove if quantity becomes 0"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart = cart_item.cart
    dish_name = cart_item.dish.name
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        message = f'Updated quantity: {cart_item.quantity} x {dish_name}'
        removed = False
    else:
        cart_item.delete()
        message = f'Removed {dish_name} from cart'
        removed = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        # Refresh cart to get updated total
        cart.refresh_from_db()
        return JsonResponse({
            'success': True,
            'quantity': 0 if removed else cart_item.quantity,
            'subtotal': 0 if removed else float(cart_item.get_subtotal()),
            'total': float(cart.get_total()),
            'removed': removed
        })
    
    messages.success(request, message)
    return redirect('main:cart_page')


# Stripe Configuration
if stripe is not None:
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


@login_required
def create_checkout_session(request):
    """Create Stripe Checkout Session and Order"""
    if stripe is None:
        messages.error(request, 'Stripe is not installed. Please install stripe package.')
        return redirect('main:cart_page')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('dish')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('main:cart_page')
    
    # Check if Stripe is configured
    if not stripe.api_key:
        messages.error(request, 'Payment processing is not configured. Please contact support.')
        return redirect('main:cart_page')
    
    # Calculate total
    total = cart.get_total()
    
    # Convert cart items to Stripe line items
    line_items = []
    for item in cart_items:
        # Stripe expects amounts in smallest currency unit (paise for INR)
        price_in_paise = int(float(item.dish.price) * 100)
        
        # Get absolute image URL if available
        image_url = None
        if item.dish.image:
            image_url = request.build_absolute_uri(item.dish.image.url)
        
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.dish.name,
                    'description': f"From {item.dish.restaurant.name}",
                    'images': [image_url] if image_url else [],
                },
                'unit_amount': price_in_paise,
            },
            'quantity': item.quantity,
        })
    
    try:
        # Create Order with PENDING status
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            payment_status='PENDING'
        )
        
        # Create Stripe Checkout Session
        success_url = request.build_absolute_uri('/checkout/success/') + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.build_absolute_uri('/checkout/cancel/')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_id': order.id,
                'user_id': request.user.id,
            },
            customer_email=request.user.email,
        )
        
        # Update order with Stripe session ID
        order.stripe_session_id = checkout_session.id
        order.save()
        
        # Redirect to Stripe Checkout
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        # Delete the order if it was created
        if 'order' in locals():
            order.delete()
        return redirect('main:cart_page')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        # Delete the order if it was created
        if 'order' in locals():
            order.delete()
        return redirect('main:cart_page')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    if stripe is None:
        return HttpResponse('Stripe is not installed', status=500)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    if not webhook_secret:
        return HttpResponse('Webhook secret not configured', status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(f'Invalid payload: {str(e)}', status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(f'Invalid signature: {str(e)}', status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the order by stripe_session_id
        try:
            order = Order.objects.get(stripe_session_id=session['id'])
            
            # Update payment status to PAID
            order.payment_status = 'PAID'
            order.save()
            
            # Move CartItems to OrderItems
            cart = order.user.cart
            cart_items = cart.items.all()
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    dish=cart_item.dish,
                    quantity=cart_item.quantity,
                    price=cart_item.dish.price  # Store price at time of order
                )
            
            # Clear the cart
            cart_items.delete()
            
        except Order.DoesNotExist:
            return HttpResponse(f'Order not found for session {session["id"]}', status=404)
        except Exception as e:
            return HttpResponse(f'Error processing order: {str(e)}', status=500)
    
    return HttpResponse(status=200)


@login_required
def checkout_success(request):
    """Thank you page after successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid checkout session.')
        return redirect('main:cart_page')
    
    try:
        # Get the order
        order = Order.objects.get(stripe_session_id=session_id, user=request.user)
        order_items = order.items.all().select_related('dish', 'dish__restaurant')
        
        # If order is PAID, check if user should be redirected to review page
        if order.payment_status == 'PAID':
            # Get the restaurant from the order items (use first restaurant if multiple)
            restaurants = set(item.dish.restaurant for item in order_items)
            if restaurants:
                restaurant = list(restaurants)[0]  # Get first restaurant
                # Check if user hasn't reviewed this restaurant yet
                if not restaurant.has_user_reviewed(request.user):
                    # Redirect to review page
                    return redirect('main:create_review', restaurant_id=restaurant.id)
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'main/success.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('main:cart_page')


@login_required
def checkout_cancel(request):
    """Cancel page when user cancels payment"""
    return render(request, 'main/cancel.html')


@login_required
def create_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    
    # Check if user already has a review
    existing_review = Review.objects.filter(user=request.user, restaurant=restaurant).first()
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            messages.error(request, 'Please select a valid rating (1-5 stars).')
            return redirect('main:create_review', restaurant_id=restaurant.id)
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Your review has been updated!')
        else:
            # Create new review
            Review.objects.create(
                user=request.user,
                restaurant=restaurant,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Thank you for your review!')
        
        return redirect('main:restaurant_reviews', restaurant_id=restaurant.id)
    
    context = {
        'restaurant': restaurant,
        'existing_review': existing_review,
    }
    return render(request, 'main/review_form.html', context)


def restaurant_reviews(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    reviews = restaurant.reviews.all().select_related('user').order_by('-created_at')
    
    average_rating = restaurant.get_average_rating()
    reviews_count = restaurant.get_reviews_count()
    user_has_reviewed = restaurant.has_user_reviewed(request.user) if request.user.is_authenticated else False
    
    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'average_rating': average_rating,
        'reviews_count': reviews_count,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'main/restaurant_reviews.html', context)