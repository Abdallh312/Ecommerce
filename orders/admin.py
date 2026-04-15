from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, ShippingMethod, OrderTracking, Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('product', 'variant', 'quantity', 'customization_text', 'created_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_sku', 'size_name', 'color_name', 'unit_price', 'total_price')
    fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price', 'customization_text')


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    readonly_fields = ('timestamp',)
    fields = ('status', 'message', 'location', 'timestamp')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key', 'offer', 'get_total_items', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at', 'offer')
    search_fields = ('session_key',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"LE {obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'email', 'status', 'payment_status', 'total_amount', 'get_item_count', 'created_at')
    list_editable = ('status', 'payment_status')
    list_filter = ('status', 'payment_status', 'created_at', 'shipped_at')
    search_fields = ('order_number', 'email', 'shipping_email', 'tracking_number')
    readonly_fields = ('id', 'order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderTrackingInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'email', 'status', 'payment_status', 'tracking_number')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'offer', 'total_amount')
        }),
        ('Shipping Address', {
            'fields': ('shipping_name', 'shipping_email', 'shipping_phone', 
                      'shipping_address_line1', 'shipping_address_line2',
                      'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        for order in queryset:
            order.send_invoice_email()
        self.message_user(request, f"Marked {queryset.count()} orders as processing and sent invoices.")
    mark_as_processing.short_description = 'Mark selected orders as processing'
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='shipped', shipped_at=timezone.now())
        for order in queryset:
            order.send_invoice_email()
        self.message_user(request, f"Marked {queryset.count()} orders as shipped and sent updates.")
    mark_as_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__order_number', 'product_name', 'product_sku')
    readonly_fields = ('product_name', 'product_sku', 'size_name', 'color_name')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'message', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__order_number', 'status', 'message')
    readonly_fields = ('timestamp',)
