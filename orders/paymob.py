"""
Paymob Payment Gateway Integration
===================================
3-step flow:
  1. POST /auth/tokens          → get auth_token
  2. POST /ecommerce/orders     → register order, get paymob_order_id
  3. POST /acceptance/payment_keys → get payment_key for the iframe
"""
import hashlib
import hmac
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

PAYMOB_BASE_URL = "https://accept.paymob.com/api"


class PaymobService:
    def __init__(self):
        self.api_key            = settings.PAYMOB_API_KEY
        self.hmac_secret        = settings.PAYMOB_HMAC_SECRET
        # Card credentials
        self.card_integration_id = settings.PAYMOB_CARD_INTEGRATION_ID
        self.card_iframe_id      = settings.PAYMOB_CARD_IFRAME_ID
        # Wallet credentials
        self.wallet_integration_id = settings.PAYMOB_WALLET_INTEGRATION_ID
        self.wallet_iframe_id      = settings.PAYMOB_WALLET_IFRAME_ID

    # ------------------------------------------------------------------
    # Step 1 – Authenticate and get a short-lived token
    # ------------------------------------------------------------------
    def get_auth_token(self):
        url  = f"{PAYMOB_BASE_URL}/auth/tokens"
        resp = requests.post(url, json={"api_key": self.api_key}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token")
        if not token:
            raise ValueError(f"Paymob auth failed: {data}")
        return token

    # ------------------------------------------------------------------
    # Step 2 – Register the order with Paymob
    # ------------------------------------------------------------------
    def register_order(self, auth_token, amount_cents, order_id, items):
        """
        amount_cents : integer – total in Egyptian Piastres (LE × 100)
        order_id     : your internal Order UUID (used as merchant_order_id)
        items        : list of dicts with name, amount_cents, quantity, description
        """
        url = f"{PAYMOB_BASE_URL}/ecommerce/orders"
        payload = {
            "auth_token":        auth_token,
            "delivery_needed":   False,
            "amount_cents":      amount_cents,
            "currency":          "EGP",
            "merchant_order_id": str(order_id),
            "items":             items,
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        paymob_order_id = data.get("id")
        if not paymob_order_id:
            raise ValueError(f"Paymob order registration failed: {data}")
        return paymob_order_id

    # ------------------------------------------------------------------
    # Step 3 – Get a payment key for the iframe
    # ------------------------------------------------------------------
    def get_payment_key(self, auth_token, paymob_order_id, amount_cents, billing_data):
        """
        billing_data keys required by Paymob:
            apartment, email, floor, first_name, last_name,
            street, building, phone_number, shipping_method,
            postal_code, city, country, state
        """
        url = f"{PAYMOB_BASE_URL}/acceptance/payment_keys"
        payload = {
            "auth_token":    auth_token,
            "amount_cents":  amount_cents,
            "expiration":    3600,
            "order_id":      paymob_order_id,
            "billing_data":  billing_data,
            "currency":      "EGP",
            "integration_id": self.integration_id,
            "lock_order_when_paid": True,
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        payment_key = data.get("token")
        if not payment_key:
            raise ValueError(f"Paymob payment key failed: {data}")
        return payment_key

    # ------------------------------------------------------------------
    # Full helper – run all 3 steps and return the iframe URL
    # ------------------------------------------------------------------
    def create_payment_url(self, order, cart_items, payment_method='wallet', wallet_phone=None):
        """
        order        : orders.models.Order instance (already saved)
        cart_items   : queryset of CartItem objects
        payment_method: 'card' or 'wallet'
        wallet_phone : mobile wallet phone number (required for wallet payments)

        Returns the Paymob iframe URL to redirect the customer to.
        """
        if payment_method == 'card':
            self.integration_id = self.card_integration_id
            self.iframe_id      = self.card_iframe_id
        else:
            self.integration_id = self.wallet_integration_id
            self.iframe_id      = self.wallet_iframe_id

        # Amount in piastres (1 LE = 100 piastres)
        amount_cents = int(order.total_amount * 100)

        # Build items list for Paymob
        items = [
            {
                "name":         item.product.name,
                "amount_cents": int(item.get_total_price() * 100),
                "description":  item.product.short_description or item.product.name,
                "quantity":     item.quantity,
            }
            for item in cart_items
        ]

        # Split shipping name into first / last
        name_parts = order.shipping_name.split(" ", 1)
        first_name = name_parts[0]
        last_name  = name_parts[1] if len(name_parts) > 1 else "N/A"

        # Use wallet phone if provided, otherwise fall back to shipping phone
        phone_number = wallet_phone or order.shipping_phone or "NA"

        billing_data = {
            "apartment":       "NA",
            "email":           order.shipping_email,
            "floor":           "NA",
            "first_name":      first_name,
            "street":          order.shipping_address_line1,
            "building":        "NA",
            "phone_number":    phone_number,
            "shipping_method": "PKG",
            "postal_code":     order.shipping_postal_code,
            "city":            order.shipping_city,
            "country":         order.shipping_country,
            "last_name":       last_name,
            "state":           order.shipping_state,
        }

        auth_token      = self.get_auth_token()
        paymob_order_id = self.register_order(auth_token, amount_cents, order.id, items)
        payment_key     = self.get_payment_key(auth_token, paymob_order_id, amount_cents, billing_data)

        iframe_url = (
            f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}"
            f"?payment_token={payment_key}"
        )
        return iframe_url

    # ------------------------------------------------------------------
    # HMAC verification for webhooks
    # ------------------------------------------------------------------
    def verify_hmac(self, data: dict, received_hmac: str) -> bool:
        """
        Concatenate the required fields in the documented order and compare
        against the HMAC-SHA512 signature sent by Paymob.
        """
        fields = [
            str(data.get("amount_cents",  "")),
            str(data.get("created_at",    "")),
            str(data.get("currency",      "")),
            str(data.get("error_occured", "")),
            str(data.get("has_parent_transaction", "")),
            str(data.get("id",            "")),
            str(data.get("integration_id","")).replace("None", ""),
            str(data.get("is_3d_secure",  "")),
            str(data.get("is_auth",       "")),
            str(data.get("is_capture",    "")),
            str(data.get("is_refunded",   "")),
            str(data.get("is_standalone_payment", "")),
            str(data.get("is_voided",     "")),
            str(data.get("order",         {}).get("id", "") if isinstance(data.get("order"), dict) else data.get("order", "")),
            str(data.get("owner",         "")),
            str(data.get("pending",       "")),
            str(data.get("source_data",   {}).get("pan",     "") if isinstance(data.get("source_data"), dict) else ""),
            str(data.get("source_data",   {}).get("sub_type","") if isinstance(data.get("source_data"), dict) else ""),
            str(data.get("source_data",   {}).get("type",    "") if isinstance(data.get("source_data"), dict) else ""),
            str(data.get("success",       "")),
        ]
        concatenated = "".join(fields)
        computed = hmac.new(
            self.hmac_secret.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(computed, received_hmac.lower())
