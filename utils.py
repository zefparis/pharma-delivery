from flask_login import current_user
from models import CartItem

def get_cart_count():
    """Get the number of items in the current user's cart"""
    if current_user.is_authenticated:
        return sum(item.quantity for item in CartItem.query.filter_by(user_id=current_user.id).all())
    return 0

def format_currency(amount):
    """Format amount as Congolese Franc"""
    return f"{amount:,.0f} FC"

def get_status_badge_class(status):
    """Get Bootstrap badge class for order status"""
    status_classes = {
        'pending': 'warning',
        'confirmed': 'info',
        'preparing': 'primary',
        'shipped': 'secondary',
        'delivered': 'success',
        'cancelled': 'danger'
    }
    return status_classes.get(status, 'secondary')
