from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from products.models import Category, Product, Size, Color, ProductVariant
from .models import Cart, CartItem, Offer, Order

class DiscountSystemTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            category=self.category,
            base_price=Decimal("100.00"),
            stock_quantity=10
        )
        self.cart = Cart.objects.create(session_key="test-session")
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )

    def test_percentage_discount(self):
        offer = Offer.objects.create(code="PERCENT20", discount_percent=Decimal("20.00"), offer_type="percentage")
        self.cart.offer = offer
        self.cart.save()
        
        # 3 * 100 = 300. 20% off 300 = 60. 300 - 60 = 240. 
        # Shipping is 90. Total = 240 + 90 = 330.
        self.assertEqual(self.cart.get_final_total(), Decimal("330.00"))

    def test_bogo_discount(self):
        offer = Offer.objects.create(code="BOGO", offer_type="bogo")
        self.cart.offer = offer
        self.cart.save()
        
        # 3 items, buy 1 get 1 free. Pay for 2.
        # 2 * 100 = 200. Shipping is 90. Total = 200 + 90 = 290.
        self.assertEqual(self.cart.get_final_total(), Decimal("290.00"))

    def test_b1g2_discount(self):
        offer = Offer.objects.create(code="B1G2", offer_type="b1g2")
        self.cart.offer = offer
        self.cart.save()
        
        # 3 items, buy 1 get 2 free. Pay for 1.
        # 1 * 100 = 100. Shipping is 90. Total = 100 + 90 = 190.
        self.assertEqual(self.cart.get_final_total(), Decimal("190.00"))

    def test_order_offer_assignment(self):
        offer = Offer.objects.create(code="OFFER10", discount_percent=Decimal("10.00"), offer_type="percentage")
        self.cart.offer = offer
        self.cart.save()
        
        client = Client()
        # Mock session
        session = client.session
        session.create()
        self.cart.session_key = session.session_key
        self.cart.save()
        
        response = client.post(reverse('orders:checkout'), {
            'shipping_name': 'Test User',
            'shipping_email': 'test@example.com',
            'shipping_address_line1': '123 Test St',
            'shipping_city': 'Test City',
            'shipping_state': 'Cairo',
            'shipping_postal_code': '12345',
            'shipping_country': 'Egypt',
            'payment_method': 'cod'
        })
        
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.offer, offer)
