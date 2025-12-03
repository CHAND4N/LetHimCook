from django.contrib import admin
from .models import Restaurant, Dish, Cuisine


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'opening_time', 'closing_time', 'created_at', 'display_cuisines', 'display_image')
    list_filter = ('created_at', 'cuisines')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    filter_horizontal = ('cuisines',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image', 'display_image', 'owner')
        }),
        ('Details', {
            'fields': ('opening_time', 'closing_time', 'iframe_location', 'cuisines')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def display_cuisines(self, obj):
        return ", ".join([cuisine.name for cuisine in obj.cuisines.all()])
    display_cuisines.short_description = 'Cuisines'
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 200px; max-height: 200px;" />'
        return "No image"
    display_image.allow_tags = True
    display_image.short_description = 'Image Preview'


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'created_at', 'display_image')
    list_filter = ('restaurant', 'created_at')
    search_fields = ('name', 'description', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('restaurant', 'name', 'description', 'price')
        }),
        ('Image', {
            'fields': ('image', 'display_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 200px; max-height: 200px;" />'
        return "No image"
    display_image.allow_tags = True
    display_image.short_description = 'Image Preview'
