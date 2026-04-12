from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage, Color, Size, ProductVariant, ProductReview, Wishlist, Announcement


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'order', 'color')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price_adjustment', 'stock_quantity', 'sku')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'description')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'name', 'category', 'base_price', 'discount_price', 'is_active', 'is_featured', 'stock_quantity', 'created_at')
    list_editable = ('is_active', 'is_featured', 'stock_quantity', 'discount_price')
    list_filter = ('category', 'is_active', 'is_featured', 'is_customizable', 'created_at')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('available_sizes', 'available_colors')
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing & Stock', {
            'fields': ('base_price', 'discount_price', 'stock_quantity', 'weight')
        }),
        ('Availability', {
            'fields': ('available_sizes', 'available_colors')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured', 'is_customizable')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        })
    )

    def get_thumbnail(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return mark_safe(f'<img src="{main_image.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    get_thumbnail.short_description = 'Thumbnail'


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code', 'color_preview')
    search_fields = ('name',)

    def color_preview(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 30px; background-color: {obj.hex_code}; border: 1px solid #ccc; border-radius: 4px;"></div>')
    color_preview.short_description = 'Preview'


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('get_image_preview', 'product', 'alt_text', 'is_main', 'order', 'color')
    list_filter = ('is_main', 'color')
    search_fields = ('product__name', 'alt_text')

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    get_image_preview.short_description = 'Preview'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'final_price', 'stock_quantity', 'sku')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'created_at', 'is_verified_purchase')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at',)

    def rating_stars(self, obj):
        return mark_safe('★' * obj.rating + '☆' * (5 - obj.rating))
    rating_stars.short_description = 'Rating'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'has_discount', 'discount_code',
                    'discount_percentage', 'is_active', 'start_date', 'end_date', 'created_at')
    list_filter = ('announcement_type', 'is_active', 'has_discount')
    search_fields = ('title', 'message', 'discount_code')
    readonly_fields = ('created_at', 'created_by')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'message', 'announcement_type')
        }),
        ('Discount', {
            'fields': ('has_discount', 'discount_code', 'discount_percentage'),
            'description': 'Fill these in only when this announcement is a promotional offer.'
        }),
        ('Scheduling', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Meta', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
