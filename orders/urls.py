from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/update-variant/', views.UpdateCartVariantView.as_view(), name='update_cart_variant'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/success/<uuid:order_id>/', views.OrderSuccessView.as_view(), name='order_success'),

    # Paymob payment
    path('paymob/initiate/', views.PaymobInitiateView.as_view(), name='paymob_initiate'),
    path('paymob/callback/response/', views.PaymobResponseCallbackView.as_view(), name='paymob_response_callback'),
    path('paymob/callback/processed/', views.PaymobProcessedCallbackView.as_view(), name='paymob_processed_callback'),
    
    # Orders
    
    path('order/<uuid:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('track/', views.TrackOrderView.as_view(), name='track_order'),
    
    # API
    path('api/products/<uuid:product_id>/variants/', views.ProductVariantsAPIView.as_view(), name='product_variants_api'),
    path('cart/count/', views.CartCountAPIView.as_view(), name='cart_count'),
    path('cart/totals/', views.CartTotalsAPIView.as_view(), name='cart_totals'),
    path('cart/apply-offer/', views.ApplyOfferView.as_view(), name='apply_offer'),
    path('cart/remove-offer/', views.RemoveOfferView.as_view(), name='remove_offer'),
]
