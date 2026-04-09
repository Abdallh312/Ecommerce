from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Product, Category, ProductVariant, Wishlist
from django.core.paginator import Paginator
import uuid


def get_session_wishlist(request):
    """Return list of UUID objects from session for anonymous users."""
    raw = request.session.get('wishlist', [])
    result = []
    for i in raw:
        try:
            result.append(uuid.UUID(i))
        except (ValueError, AttributeError):
            pass
    return result


def get_user_wishlist_ids(request):
    """Return wishlist IDs for both authenticated and anonymous users."""
    if request.user.is_authenticated:
        return list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    return get_session_wishlist(request)


class HomeView(ListView):
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'featured_products'
    
    def get_queryset(self):
        return Product.objects.filter(is_featured=True, is_active=True)[:8]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:6]
        context['new_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
        context['user_wishlist_ids'] = get_user_wishlist_ids(self.request)
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Sort by price, name, etc.
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['base_price', '-base_price', 'name', '-name', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['user_wishlist_ids'] = get_user_wishlist_ids(self.request)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get available variants
        context['variants'] = product.variants.all()
        context['sizes'] = product.available_sizes.all()
        context['colors'] = product.available_colors.all()
        
        # Get related products
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # Get reviews
        context['reviews'] = product.reviews.all()[:5]
        
        context['user_wishlist_ids'] = get_user_wishlist_ids(self.request)
        return context


class CategoryProductsView(ListView):
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Product.objects.filter(category=category, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        context['user_wishlist_ids'] = get_user_wishlist_ids(self.request)
        return context


class SearchView(ListView):
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) | 
                Q(short_description__icontains=query),
                is_active=True
            )
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['user_wishlist_ids'] = get_user_wishlist_ids(self.request)
        return context


class ProductVariantsAPIView(View):
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            variants = ProductVariant.objects.filter(product=product)
            
            variants_data = []
            for variant in variants:
                variants_data.append({
                    'id': variant.id,
                    'size': variant.size.name,
                    'color': variant.color.name,
                    'color_hex': variant.color.hex_code,
                    'price': str(variant.final_price),
                    'stock': variant.stock_quantity,
                    'sku': variant.sku
                })
            
            return JsonResponse({
                'success': True,
                'variants': variants_data
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class WishlistListView(ListView):
    """Shows wishlist for both logged-in users (DB) and guests (session)."""
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return []  # We build listing in get_context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            items = Wishlist.objects.filter(user=self.request.user).select_related('product')
            context['wishlist_items'] = items
        else:
            session_ids = get_session_wishlist(self.request)
            products = Product.objects.filter(id__in=session_ids, is_active=True)
            # Wrap in dicts to match the template's `item.product` pattern
            context['wishlist_items'] = [{'product': p} for p in products]
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ToggleWishlistView(View):
    """Toggle wishlist for both logged-in and anonymous users."""
    def post(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            pid_str = str(product.id)

            if request.user.is_authenticated:
                wishlist_item, created = Wishlist.objects.get_or_create(
                    user=request.user, product=product
                )
                if not created:
                    wishlist_item.delete()
                    message = 'Product removed from favorites.'
                    is_favorite = False
                else:
                    message = 'Product added to favorites.'
                    is_favorite = True
            else:
                # Session-based wishlist for anonymous users
                wishlist = request.session.get('wishlist', [])
                if pid_str in wishlist:
                    wishlist.remove(pid_str)
                    message = 'Product removed from favorites.'
                    is_favorite = False
                else:
                    wishlist.append(pid_str)
                    message = 'Product added to favorites.'
                    is_favorite = True
                request.session['wishlist'] = wishlist
                request.session.modified = True

            return JsonResponse({
                'success': True,
                'message': message,
                'is_favorite': is_favorite
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
