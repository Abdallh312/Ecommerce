# Pilot - Softwear Store

A modern Django-based e-commerce platform for softwear customization, featuring a dark theme and comprehensive product management system.

## Features

### 🛍️ Core E-commerce Features
- **Product Catalog**: Browse products with filtering and search
- **Product Variants**: Support for sizes, colors, and customization options
- **Shopping Cart**: Add, update, and remove items from cart
- **Checkout System**: Complete order processing with customer information
- **Order Management**: Track orders and order history
- **Email Invoices**: Automatic invoice generation and sending

### 🎨 Design & UI
- **Dark Theme**: Modern softwear-inspired black and white design
- **Responsive Design**: Mobile-friendly layout using Bootstrap 5
- **Interactive Elements**: Smooth animations and hover effects
- **Product Gallery**: Multiple images with thumbnail navigation

### 📦 Product Management
- **Multiple Images**: Support for product image galleries
- **Size & Color Variants**: Comprehensive variant system
- **Stock Management**: Track inventory for each variant
- **Customization**: Allow customers to add custom text/designs
- **Categories**: Organize products by category

### 💳 Order Processing
- **Cart Persistence**: Session-based cart for guests, database for users
- **Order Tracking**: Complete order lifecycle management
- **Invoice System**: Professional email invoices with order details
- **Admin Dashboard**: Comprehensive order management interface

## Installation

### Prerequisites
- Python 3.8 or higher
- Django 4.2+
- Pillow (for image handling)

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd streetwear_store
   ```

2. **Install dependencies**
   ```bash
   pip install django pillow
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Create media directories**
   ```bash
   mkdir media
   mkdir media/products
   mkdir media/categories
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Admin credentials: username: `admin`, password: `admin123`

## Project Structure

```
streetwear_store/
├── streetwear_store/          # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── products/                 # Product management app
│   ├── models.py            # Product, Category, Color, Size models
│   ├── views.py             # Product catalog views
│   ├── urls.py              # Product URLs
│   └── admin.py             # Product admin configuration
├── orders/                   # Order management app
│   ├── models.py            # Cart, Order, OrderItem models
│   ├── views.py             # Cart and checkout views
│   ├── urls.py              # Order URLs
│   └── admin.py             # Order admin configuration
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── products/            # Product templates
│   └── orders/              # Order templates
├── static/                   # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Static images
├── media/                    # User uploaded files
└── manage.py                # Django management script
```

## Models Overview

### Product Models
- **Category**: Product categories (T-shirts, Hoodies, etc.)
- **Product**: Main product information
- **ProductImage**: Multiple images per product
- **Color**: Available colors with hex codes
- **Size**: Available sizes (S, M, L, XL, etc.)
- **ProductVariant**: Size/color combinations with pricing and stock
- **ProductReview**: Customer reviews and ratings
- **Wishlist**: User wishlists

### Order Models
- **Cart**: Shopping cart for users/sessions
- **CartItem**: Individual items in cart
- **Order**: Customer orders with shipping info
- **OrderItem**: Items within an order
- **OrderTracking**: Order status updates
- **ShippingMethod**: Available shipping options

## Admin Interface

The admin interface provides comprehensive management tools:

### Products Management
- Add/edit products with multiple images
- Manage categories, sizes, and colors
- Set up product variants with different pricing
- Monitor stock levels
- Manage product reviews

### Orders Management
- View and process orders
- Update order status
- Add tracking information
- Generate shipping labels
- View order analytics

### Customer Management
- View customer information
- Monitor cart contents
- Track customer orders
- Manage wishlists

## Email Configuration

The system is configured to send email invoices. Update the following settings in `settings.py` for production:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'Pilot <noreply@pilot.com>'
```

## Customization

### Styling
- Main CSS file: `static/css/style.css`
- Dark theme with CSS variables for easy customization
- Bootstrap 5 integration for responsive design

### Templates
- Base template with navigation and footer
- Modular template structure for easy modifications
- Dark theme optimized for softwear aesthetic

### JavaScript
- Interactive cart functionality
- Product variant selection
- Form validation
- AJAX-based operations

## API Endpoints

### Product API
- `/api/product-variants/<product_id>/` - Get product variants

### Cart API
- `/orders/cart/add/` - Add item to cart
- `/orders/cart/update/` - Update cart quantities
- `/orders/cart/remove/<item_id>/` - Remove item from cart

## Production Deployment

For production deployment:

1. **Update settings**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Set up proper database (PostgreSQL recommended)
   - Configure static file serving

2. **Security**
   - Use environment variables for sensitive settings
   - Set up SSL/HTTPS
   - Configure secure session cookies

3. **Media Files**
   - Configure proper media file storage
   - Set up CDN for static files
   - Optimize images for web

## Support

For issues or questions regarding this project, please check the admin interface for comprehensive management tools or refer to the Django documentation for framework-specific questions.

## License

This project is developed for educational purposes. Please ensure proper licensing for production use.

---

**Pilot 2024** - Premium Streetwear Customization Platform
"# pilotshopkidwear" 
