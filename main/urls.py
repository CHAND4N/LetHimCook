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
]

