from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurant/create/', views.create_restaurant, name='create_restaurant'),
    path('restaurant/<int:restaurant_id>/update/', views.update_restaurant, name='update_restaurant'),
    path('restaurant/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('restaurant/<int:restaurant_id>/dish/add/', views.add_dish, name='add_dish'),
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('dish/<int:dish_id>/update/', views.update_dish, name='update_dish'),
    path('dish/<int:dish_id>/delete/', views.delete_dish, name='delete_dish'),
    path('explore/', views.explore, name='explore'),
    path('allrestaurants/', views.all_restaurants, name='admin_restaurants'),
    path('cart/add/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/item/<int:item_id>/increment/', views.increment_item, name='increment_item'),
    path('cart/item/<int:item_id>/decrement/', views.decrement_item, name='decrement_item'),
    path('checkout/create/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('restaurant/<int:restaurant_id>/review/', views.create_review, name='create_review'),
    path('restaurant/<int:restaurant_id>/reviews/', views.restaurant_reviews, name='restaurant_reviews'),
    path('about/', views.about_us, name='about_us'),
]

