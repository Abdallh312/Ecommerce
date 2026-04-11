from django.contrib import admin
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
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'is_featured', 'stock_quantity', 'created_at')
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
            'fields': ('base_price', 'stock_quantity', 'weight')
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


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name',)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_main', 'order', 'color')
    list_filter = ('is_main', 'color')
    search_fields = ('product__name', 'alt_text')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'final_price', 'stock_quantity', 'sku')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'is_verified_purchase')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at',)


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
