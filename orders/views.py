from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, CreateView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Cart, CartItem, Order, OrderItem, Offer
from products.models import Product, ProductVariant
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)


class CartMixin:
    """Mixin to handle cart operations"""
    
    def get_cart(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


class CartView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        return render(request, 'orders/cart.html', {'cart': cart})


class AddToCartView(CartMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            variant_id = data.get('variant_id')
            size = data.get('size')
            color = data.get('color')
            quantity = int(data.get('quantity', 1))
            customization_text = data.get('customization_text', '')
            
            # Validate quantity
            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Quantity must be at least 1'
                })
            
            product = get_object_or_404(Product, id=product_id)
            variant = None
            
            # Use variant_id if provided, otherwise find by size/color
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id)
            elif size and color:
                from products.models import Size, Color
                try:
                    # Get Size and Color objects by ID
                    size_obj = get_object_or_404(Size, id=size)
                    color_obj = get_object_or_404(Color, id=color)
                    
                    variant = ProductVariant.objects.get(
                        product=product,
                        size=size_obj,
                        color=color_obj
                    )
                except ProductVariant.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Selected variant not available'
                    })
            
            # Check stock availability
            available_stock = variant.stock_quantity if variant else product.stock_quantity
            if quantity > available_stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {available_stock} items available in stock'
                })
            
            cart = self.get_cart(request)
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                customization_text=customization_text,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Check if adding this quantity would exceed stock
                new_total_quantity = cart_item.quantity + quantity
                if new_total_quantity > available_stock:
                    return JsonResponse({
                        'success': False,
                        'error': f'Cannot add {quantity} more items. Only {available_stock} items available in stock'
                    })
                
                cart_item.quantity = new_total_quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart successfully!',
                'cart_total': cart.get_total_items()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class UpdateCartView(CartMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            # Validate quantity
            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Quantity must be at least 1'
                })
            
            cart = self.get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Check stock availability
            available_stock = cart_item.variant.stock_quantity if cart_item.variant else cart_item.product.stock_quantity
            if quantity > available_stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {available_stock} items available in stock'
                })
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_items(),
                'subtotal': str(cart.get_total_price()),
                'total': str(cart.get_final_total())
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class UpdateCartVariantView(CartMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            variant_id = data.get('variant_id')
            
            cart = self.get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id)
                
                # Check if this variant already exists in cart for the same product
                existing_item = CartItem.objects.filter(
                    cart=cart,
                    product=cart_item.product,
                    variant=variant,
                    customization_text=cart_item.customization_text
                ).exclude(id=item_id).first()
                
                if existing_item:
                    # Merge quantities and delete current item
                    existing_item.quantity += cart_item.quantity
                    existing_item.save()
                    cart_item.delete()
                else:
                    # Update current item with new variant
                    cart_item.variant = variant
                    cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart item variant updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class RemoveFromCartView(CartMixin, View):
    def post(self, request, item_id):
        try:
            cart = self.get_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

from django.db import transaction
class CheckoutView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        return render(request, 'orders/checkout.html', {'cart': cart})
    def post(self, request):
        cart = self.get_cart(request)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        # Get form data
        data = request.POST
        payment_method = data.get('payment_method', 'cod')
        shipping_state = data.get('shipping_state', '')
        
        # Validate required fields
        required_fields = [
            'shipping_name', 'shipping_email', 'shipping_address_line1',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            messages.error(request, f'Please fill in all required fields: {", ".join(missing_fields)}')
            return render(request, 'orders/checkout.html', {'cart': cart})
        
        # Calculate totals
        subtotal = cart.get_total_price()
        tax_amount = Decimal('0.00')  # No tax
        shipping_state = data.get('shipping_state', '')
        shipping_cost = cart.get_shipping_cost(shipping_state)  # Dynamic based on state
        total_amount = cart.get_final_total(shipping_state)
        
        # Set payment status based on payment method
        payment_status = 'pending' if payment_method == 'cod' else 'paid'
        
        # Create order
        order = Order.objects.create(
            email=data.get('shipping_email'),
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            payment_status=payment_status,
            shipping_name=data.get('shipping_name'),
            shipping_email=data.get('shipping_email'),
            shipping_phone=data.get('shipping_phone', ''),
            shipping_address_line1=data.get('shipping_address_line1'),
            shipping_address_line2=data.get('shipping_address_line2', ''),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_postal_code=data.get('shipping_postal_code'),
            shipping_country=data.get('shipping_country'),
            notes=data.get('notes', ''),
        )
        
        # Validate stock availability before creating order
        for cart_item in cart.items.all():
            if cart_item.variant:
                # Check specific variant (size/color combination) stock
                available_stock = cart_item.variant.stock_quantity
                variant_info = f"{cart_item.variant.size.name} / {cart_item.variant.color.name}"
                if cart_item.quantity > available_stock:
                    messages.error(request, f'Not enough stock for {cart_item.product.name} ({variant_info}). Only {available_stock} available.')
                    order.delete()  # Delete order if stock not available
                    return render(request, 'orders/checkout.html', {'cart': cart})
            else:
                # Fallback to general product stock if no variant
                available_stock = cart_item.product.stock_quantity
                if cart_item.quantity > available_stock:
                    messages.error(request, f'Not enough stock for {cart_item.product.name}. Only {available_stock} available.')
                    order.delete()  # Delete order if stock not available
                    return render(request, 'orders/checkout.html', {'cart': cart})
        
        # Create order items and reduce specific variant stock
        for cart_item in cart.items.all():
            unit_price = cart_item.variant.final_price if cart_item.variant else cart_item.product.base_price
            total_price = unit_price * cart_item.quantity
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=total_price,
                customization_text=cart_item.customization_text,
                product_name=cart_item.product.name,
                product_sku=cart_item.variant.sku if cart_item.variant else '',
                size_name=cart_item.variant.size.name if cart_item.variant else '',
                color_name=cart_item.variant.color.name if cart_item.variant else '',
            )
            
            # Reduce product and variant stock
            if cart_item.variant and cart_item.variant.stock_quantity >= cart_item.quantity:
                cart_item.variant.stock_quantity -= cart_item.quantity
                cart_item.variant.save()
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            else:
                pass
        
        # Send invoice email
        self.send_invoice_email(order)
        
        # Clear cart
        cart.items.all().delete()
        
        # Show success message
        payment_method_display = {
            'card': 'Credit/Debit Card',
            'wallet': 'Mobile Wallet',
            'paypal': 'PayPal',
            'cod': 'Cash on Delivery'
        }.get(payment_method, 'Unknown')
        
        messages.success(
            request, 
            f'Order {order.order_number} placed successfully! Payment method: {payment_method_display}. '
            f'Confirmation email sent to {order.shipping_email}'
        )
        
        return redirect('orders:order_success', order_id=order.id)
    
    def send_invoice_email(self, order):
        """Send invoice email to customer"""
        try:
            subject = f'Order Confirmation - {order.order_number}'
            html_message = render_to_string('orders/email/invoice.html', {'order': order})
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.shipping_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send invoice email: {e}")


class OrderSuccessView(DetailView):
    model = Order
    template_name = 'orders/order_success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'




class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'


class TrackOrderView(View):
    def get(self, request):
        return render(request, 'orders/track_order.html')

    def post(self, request):
        order_number = request.POST.get('order_number', '').strip()

        if not order_number:
            messages.error(request, 'Please provide an order number.')
            return render(request, 'orders/track_order.html')

        try:
            # Find order by number only
            order = Order.objects.get(order_number__iexact=order_number)
            return redirect('orders:order_detail', order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, 'No order found with that order number. Please check and try again.')
            return render(request, 'orders/track_order.html')


class ProductVariantsAPIView(View):
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            variants = []
            
            for variant in product.variants.all():
                variants.append({
                    'id': variant.id,
                    'size_id': variant.size.id if variant.size else None,
                    'size_name': variant.size.name if variant.size else '',
                    'color_id': variant.color.id if variant.color else None,
                    'color_name': variant.color.name if variant.color else '',
                    'price': str(variant.final_price),
                    'stock': variant.stock_quantity
                })
            
            return JsonResponse({
                'success': True,
                'variants': variants
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class CartCountAPIView(CartMixin, View):
    def get(self, request):
        try:
            cart = self.get_cart(request)
            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_items()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class CartTotalsAPIView(CartMixin, View):
    def get(self, request):
        try:
            cart = self.get_cart(request)
            return JsonResponse({
                'success': True,
                'subtotal': str(cart.get_total_price()),
                'shipping_cost': str(cart.get_shipping_cost()),
                'total': str(cart.get_final_total()),
                'discount_percent': str(cart.offer.discount_percent) if cart.offer and cart.offer.is_active else '0',
                'item_count': cart.get_total_items()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

class ApplyOfferView(CartMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            
            cart = self.get_cart(request)
            
            if not code:
                # Remove offer if empty code is sent
                cart.offer = None
                cart.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Offer removed',
                    'subtotal': str(cart.get_total_price()),
                    'shipping_cost': str(cart.get_shipping_cost()),
                    'total': str(cart.get_final_total())
                })
                
            try:
                offer = Offer.objects.get(code__iexact=code, is_active=True)
                cart.offer = offer
                cart.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Offer applied! {offer.discount_percent}% off',
                    'subtotal': str(cart.get_total_price()),
                    'shipping_cost': str(cart.get_shipping_cost()),
                    'total': str(cart.get_final_total()),
                    'discount_percent': str(offer.discount_percent)
                })
            except Offer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid or expired offer code'
                })
                
        except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })


class RemoveOfferView(CartMixin, View):
    def post(self, request):
        try:
            cart = self.get_cart(request)
            cart.offer = None
            cart.save()
            return JsonResponse({
                'success': True,
                'message': 'Offer removed',
                'subtotal': str(cart.get_total_price()),
                'total': str(cart.get_final_total())
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# =============================================================================
# Paymob Payment Views
# =============================================================================

class PaymobInitiateView(CartMixin, View):
    """Step 1: Collect checkout form, create order, redirect to Paymob iframe."""

    def post(self, request):
        from .paymob import PaymobService
        cart = self.get_cart(request)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('orders:cart')

        data = request.POST
        payment_method = data.get('payment_method', 'cod')
        shipping_state = data.get('shipping_state', '')

        # Validate required fields
        required_fields = [
            'shipping_name', 'shipping_email', 'shipping_address_line1',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
        ]
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            messages.error(request, f'Please fill in all required fields: {", ".join(missing_fields)}')
            return render(request, 'orders/checkout.html', {'cart': cart})

        # If COD, delegate to existing CheckoutView
        if payment_method not in ['card', 'wallet']:
            return CheckoutView.as_view()(request)

        # --- Card payment via Paymob ---
        subtotal      = cart.get_total_price()
        shipping_cost = cart.get_shipping_cost(shipping_state)
        total_amount  = cart.get_final_total(shipping_state)

        # Create order with pending payment status
        order = Order.objects.create(
            email                  = data.get('shipping_email'),
            subtotal               = subtotal,
            shipping_cost          = shipping_cost,
            total_amount           = total_amount,
            payment_status         = 'pending',
            shipping_name          = data.get('shipping_name'),
            shipping_email         = data.get('shipping_email'),
            shipping_phone         = data.get('shipping_phone', ''),
            shipping_address_line1 = data.get('shipping_address_line1'),
            shipping_address_line2 = data.get('shipping_address_line2', ''),
            shipping_city          = data.get('shipping_city'),
            shipping_state         = shipping_state,
            shipping_postal_code   = data.get('shipping_postal_code'),
            shipping_country       = data.get('shipping_country'),
            notes                  = data.get('notes', ''),
        )

        # Create order items (stock reduced only on payment success)
        for cart_item in cart.items.all():
            unit_price  = cart_item.variant.final_price if cart_item.variant else cart_item.product.base_price
            total_price = unit_price * cart_item.quantity
            OrderItem.objects.create(
                order               = order,
                product             = cart_item.product,
                variant             = cart_item.variant,
                quantity            = cart_item.quantity,
                unit_price          = unit_price,
                total_price         = total_price,
                customization_text  = cart_item.customization_text,
                product_name        = cart_item.product.name,
                product_sku         = cart_item.variant.sku if cart_item.variant else '',
                size_name           = cart_item.variant.size.name if cart_item.variant else '',
                color_name          = cart_item.variant.color.name if cart_item.variant else '',
            )

        # Stash order id in session so callback can find it
        request.session['pending_paymob_order_id'] = str(order.id)

        try:
            paymob       = PaymobService()
            wallet_phone = data.get('wallet_phone', '').strip() if payment_method == 'wallet' else None
            iframe_url   = paymob.create_payment_url(order, cart.items.all(), payment_method=payment_method, wallet_phone=wallet_phone)
            return redirect(iframe_url)
        except Exception as exc:
            logger.exception('Paymob initiation failed: %s', exc)
            order.delete()
            messages.error(request, 'Could not connect to payment gateway. Please try again or use Cash on Delivery.')
            return redirect('orders:checkout')


class PaymobResponseCallbackView(View):
    """
    Paymob redirects the customer browser here after the card form.
    GET /orders/paymob/callback/response/?success=true&id=...&order=...
    """

    def get(self, request):
        success = request.GET.get('success', 'false').lower() == 'true'
        pending = request.GET.get('pending', 'false').lower() == 'true'

        order_id = request.session.get('pending_paymob_order_id')
        if not order_id:
            messages.error(request, 'Session expired. Please check your orders.')
            return redirect('products:home')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('products:home')

        if success:
            order.payment_status = 'paid'
            order.status         = 'processing'
            order.save()

            # Reduce stock
            for item in order.items.all():
                if item.variant and item.variant.stock_quantity >= item.quantity:
                    item.variant.stock_quantity -= item.quantity
                    item.variant.save()
                    item.product.stock_quantity -= item.quantity
                    item.product.save()

            # Clear the cart
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if cart:
                cart.items.all().delete()

            request.session.pop('pending_paymob_order_id', None)

            # Send confirmation email
            try:
                subject      = f'Order Confirmation - {order.order_number}'
                html_message = render_to_string('orders/email/invoice.html', {'order': order})
                plain_message = strip_tags(html_message)
                send_mail(
                    subject       = subject,
                    message       = plain_message,
                    html_message  = html_message,
                    from_email    = settings.DEFAULT_FROM_EMAIL,
                    recipient_list= [order.shipping_email],
                    fail_silently = True,
                )
            except Exception as exc:
                logger.exception('Failed to send confirmation email: %s', exc)

            messages.success(request, f'Payment successful! Order {order.order_number} confirmed.')
            return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))
            
        # If it's pending (like wallet payments), we shouldn't mark it failed just yet
        if pending:
            messages.info(request, 'Payment is processing. Please complete the authorization on your phone if required.')
            return redirect('orders:order_success', order_id=order.id)
            
        txn_response_code = request.GET.get('txn_response_code', 'Unknown')
        data_message = request.GET.get('data.message', 'Transaction declined by gateway')
        
        order.payment_status = 'failed'
        order.save()
        request.session.pop('pending_paymob_order_id', None)
        
        error_msg = f'Payment was not completed ({txn_response_code}: {data_message}). Please try again or use Cash on Delivery.'
        messages.error(request, error_msg)
        return redirect('orders:checkout')


@method_decorator(csrf_exempt, name='dispatch')
class PaymobProcessedCallbackView(View):
    """
    Server-to-server POST from Paymob after every transaction event.
    GET /orders/paymob/callback/processed/?hmac=...
    Body: JSON transaction object
    """

    def post(self, request):
        from .paymob import PaymobService
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            payload = request.POST.dict()

        received_hmac = request.GET.get('hmac', '')
        obj = payload.get('obj', payload)

        paymob = PaymobService()
        if received_hmac and not paymob.verify_hmac(obj, received_hmac):
            logger.warning('Paymob HMAC verification failed')
            return HttpResponse(status=403)

        success = str(obj.get('success', '')).lower() == 'true'
        pending = str(obj.get('pending', '')).lower() == 'true'

        paymob_order = obj.get('order', {})
        merchant_order_id = paymob_order.get('merchant_order_id') if isinstance(paymob_order, dict) else None

        if not merchant_order_id:
            return HttpResponse(status=200)

        try:
            order = Order.objects.get(id=merchant_order_id)
        except Order.DoesNotExist:
            logger.warning('Paymob webhook: order %s not found', merchant_order_id)
            return HttpResponse(status=200)

        if success and not pending:
            if order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.status         = 'processing'
                order.save()
                logger.info('Order %s marked paid via Paymob webhook', order.order_number)
        elif not success and not pending:
            if order.payment_status == 'pending':
                order.payment_status = 'failed'
                order.save()

        return HttpResponse(status=200)
