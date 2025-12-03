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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Dishes'
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
