from .models import Cart

def cart_count_processor(request):
    """Provides the total number of items in the current user's cart."""
    try:
        session_key = request.session.session_key
        if not session_key:
            return {'cart_item_count': 0}
        
        cart = Cart.objects.filter(session_key=session_key).first()
        if cart:
            return {'cart_item_count': cart.get_total_items() or 0}
    except Exception:
        pass
        
    return {'cart_item_count': 0}
