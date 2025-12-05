from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    iframe_location = models.TextField(help_text="Embedded map iframe code", blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Calculate average rating from all reviews"""
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        return result['rating__avg'] if result['rating__avg'] else 0
    
    def get_reviews_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def has_user_reviewed(self, user):
        """Check if user has already reviewed this restaurant"""
        if not user.is_authenticated:
            return False
        return self.reviews.filter(user=user).exists()


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Dishes'
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'dish']
    
    def __str__(self):
        return f"{self.quantity} x {self.dish.name} in {self.cart.user.username}'s cart"
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.dish.price * self.quantity


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - ${self.total_price}"
    
    def get_status_display_class(self):
        """Return CSS class for status display"""
        status_classes = {
            'PENDING': 'status-pending',
            'PAID': 'status-paid',
            'FAILED': 'status-failed',
            'CANCELLED': 'status-cancelled',
        }
        return status_classes.get(self.payment_status, '')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity} x {self.dish.name} in Order #{self.order.id}"
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.price * self.quantity


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'restaurant']  # One review per user per restaurant
    
    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} - {self.rating}★"