from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Product catalog
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/', views.CategoryProductsView.as_view(), name='category_products'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # API endpoints for AJAX
    path('api/product-variants/<uuid:product_id>/', views.ProductVariantsAPIView.as_view(), name='product_variants_api'),
    
    # Wishlist
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist'),
    path('wishlist/toggle/<uuid:product_id>/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),
]
