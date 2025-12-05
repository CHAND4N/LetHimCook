from django.contrib import admin
from .models import Restaurant, Dish, Cuisine, Cart, CartItem, Order, OrderItem, Review


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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'get_item_count', 'get_total')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'
    
    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('dish', 'cart', 'quantity', 'get_subtotal', 'created_at')
    list_filter = ('created_at', 'cart__user')
    search_fields = ('dish__name', 'cart__user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('get_subtotal',)
    extra = 0
    
    def get_subtotal(self, obj):
        if obj.id:
            return f"${obj.get_subtotal():.2f}"
        return "-"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'payment_status', 'created_at', 'stripe_session_id')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_session_id', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'total_price', 'payment_status', 'stripe_session_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'dish', 'quantity', 'price', 'get_subtotal')
    list_filter = ('order__payment_status', 'order__created_at')
    search_fields = ('order__id', 'dish__name', 'order__user__username')
    readonly_fields = ('get_subtotal',)
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'rating', 'created_at', 'has_comment')
    list_filter = ('rating', 'created_at', 'restaurant')
    search_fields = ('user__username', 'restaurant__name', 'comment')
    readonly_fields = ('created_at',)
    
    def has_comment(self, obj):
        return bool(obj.comment)
    has_comment.boolean = True
    has_comment.short_description = 'Has Comment'
