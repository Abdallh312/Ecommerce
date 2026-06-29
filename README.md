# 🛍️ Pilot E-Commerce Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg?logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg?logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A modern, full-featured Django-based e-commerce platform tailored for clothing and streetwear brands. Features a sleek dark theme, comprehensive product variant management, and a seamless checkout experience.

## ✨ Key Features

### 🛒 E-commerce Core
* **Dynamic Product Catalog:** Advanced filtering, searching, and pagination.
* **Variant Management:** Robust support for sizes, colors, and customizations.
* **Shopping Cart & Checkout:** Persistent guest and authenticated user carts.
* **Order Tracking:** Complete lifecycle management with automated email invoices.

### 🎨 Design & UI
* **Modern Dark Theme:** A premium streetwear-inspired aesthetic.
* **Responsive Layout:** Mobile-first approach using Bootstrap 5.
* **Interactive Elements:** Smooth animations, micro-interactions, and a multi-image product gallery.

### ⚙️ Admin & Backend
* **Dashboard:** Comprehensive order and product management interface.
* **Inventory Tracking:** Stock management per product variant.
* **API Integration:** Ready-to-use endpoints for cart and variant operations.

## 🚀 Quick Start

### Prerequisites
* Python 3.8+
* Django 4.2+
* Pillow (for image processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abdallh312/Ecommerce.git
   cd Ecommerce
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(Alternatively: `pip install django pillow`)*

3. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Prepare Media Directories**
   ```bash
   mkdir -p media/products media/categories
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```
   * App: `http://127.0.0.1:8000/`
   * Admin: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```text
├── core/                # Core configurations & utilities
├── products/            # Catalog, categories, variants, and reviews
├── orders/              # Cart, checkout, and order tracking
├── streetwear_store/    # Main Django settings and URLs
├── templates/           # HTML templates (Base, Products, Orders)
├── static/              # CSS, JS, and UI assets
└── media/               # User-uploaded content (images)
```

## 🛠️ Configuration

### Email Settings (settings.py)
To enable automated order invoices, configure your SMTP settings:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Production Deployment
* Set `DEBUG = False`
* Configure `ALLOWED_HOSTS`
* Use PostgreSQL instead of SQLite
* Set up a WSGI/ASGI server (e.g., Gunicorn) and a reverse proxy (e.g., Nginx)

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Abdallh312/Ecommerce/issues).

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
