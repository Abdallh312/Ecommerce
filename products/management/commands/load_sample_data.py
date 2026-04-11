from django.core.management.base import BaseCommand
from products.models import Category, Product, Color, Size, ProductVariant
from decimal import Decimal


class Command(BaseCommand):
    help = 'Load sample data for the softwear store'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading sample data...'))
        
        # Create categories
        categories_data = [
            {'name': 'T-Shirts', 'slug': 't-shirts', 'description': 'Premium softwear t-shirts with custom designs'},
            {'name': 'Hoodies', 'slug': 'hoodies', 'description': 'Comfortable hoodies perfect for any season'},
            {'name': 'Pants', 'slug': 'pants', 'description': 'Stylish softwear pants and joggers'},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Complete your look with our accessories'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create colors
        colors_data = [
            {'name': 'Black', 'hex_code': '#000000'},
            {'name': 'White', 'hex_code': '#FFFFFF'},
            {'name': 'Gray', 'hex_code': '#808080'},
            {'name': 'Red', 'hex_code': '#FF0000'},
            {'name': 'Navy', 'hex_code': '#000080'},
        ]
        
        for color_data in colors_data:
            color, created = Color.objects.get_or_create(
                name=color_data['name'],
                defaults={'hex_code': color_data['hex_code']}
            )
            if created:
                self.stdout.write(f'Created color: {color.name}')
        
        # Create sizes
        sizes_data = [
            {'name': 'S', 'description': 'Small'},
            {'name': 'M', 'description': 'Medium'},
            {'name': 'L', 'description': 'Large'},
            {'name': 'XL', 'description': 'Extra Large'},
            {'name': 'XXL', 'description': 'Double Extra Large'},
        ]
        
        for size_data in sizes_data:
            size, created = Size.objects.get_or_create(
                name=size_data['name'],
                defaults={'description': size_data['description']}
            )
            if created:
                self.stdout.write(f'Created size: {size.name}')
        
        # Create sample products
        products_data = [
            {
                'name': 'Urban Logo Tee',
                'slug': 'urban-logo-tee',
                'category_slug': 't-shirts',
                'description': 'Premium cotton t-shirt featuring the Pilot logo. Perfect for everyday softwear.',
                'short_description': 'Premium cotton tee with iconic logo design',
                'base_price': Decimal('29.99'),
                'is_featured': True,
                'is_customizable': True,
                'stock_quantity': 50,
            },
            {
                'name': 'Black Hoodie',
                'slug': 'black-hoodie',
                'category_slug': 'hoodies',
                'description': 'Comfortable black hoodie made from premium materials. Features embroidered logo and kangaroo pocket.',
                'short_description': 'Classic black hoodie with premium comfort',
                'base_price': Decimal('59.99'),
                'is_featured': True,
                'is_customizable': True,
                'stock_quantity': 30,
            },
            {
                'name': 'Softwear Cargo Pants',
                'slug': 'softwear-cargo-pants',
                'category_slug': 'pants',
                'description': 'Tactical-inspired cargo pants with multiple pockets. Perfect for urban exploration.',
                'short_description': 'Tactical cargo pants with urban style',
                'base_price': Decimal('79.99'),
                'is_featured': False,
                'is_customizable': False,
                'stock_quantity': 25,
            },
            {
                'name': 'Custom Print Tee',
                'slug': 'custom-print-tee',
                'category_slug': 't-shirts',
                'description': 'Design your own custom t-shirt with our premium printing service. High-quality materials guaranteed.',
                'short_description': 'Create your own custom design',
                'base_price': Decimal('39.99'),
                'is_featured': True,
                'is_customizable': True,
                'stock_quantity': 100,
            },
            {
                'name': 'VLOM Baseball Cap',
                'slug': 'vlom-baseball-cap',
                'category_slug': 'accessories',
                'description': 'Adjustable baseball cap with VLOM embroidery. One size fits all.',
                'short_description': 'Premium baseball cap with embroidered logo',
                'base_price': Decimal('24.99'),
                'is_featured': False,
                'is_customizable': False,
                'stock_quantity': 40,
            },
        ]
        
        for prod_data in products_data:
            category = Category.objects.get(slug=prod_data['category_slug'])
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'category': category,
                    'description': prod_data['description'],
                    'short_description': prod_data['short_description'],
                    'base_price': prod_data['base_price'],
                    'is_featured': prod_data['is_featured'],
                    'is_customizable': prod_data['is_customizable'],
                    'stock_quantity': prod_data['stock_quantity'],
                    'meta_title': f"{prod_data['name']} - Pilot",
                    'meta_description': prod_data['short_description'],
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')
                
                # Add sizes and colors to products
                if prod_data['category_slug'] in ['t-shirts', 'hoodies']:
                    sizes = Size.objects.filter(name__in=['S', 'M', 'L', 'XL', 'XXL'])
                    colors = Color.objects.filter(name__in=['Black', 'White', 'Gray'])
                    product.available_sizes.set(sizes)
                    product.available_colors.set(colors)
                elif prod_data['category_slug'] == 'pants':
                    sizes = Size.objects.filter(name__in=['M', 'L', 'XL', 'XXL'])
                    colors = Color.objects.filter(name__in=['Black', 'Navy'])
                    product.available_sizes.set(sizes)
                    product.available_colors.set(colors)
                
                # Create some product variants for t-shirts and hoodies
                if prod_data['category_slug'] in ['t-shirts', 'hoodies']:
                    variant_count = 0
                    for size in product.available_sizes.all():
                        for color in product.available_colors.all():
                            sku = f"{product.slug.upper()}-{size.name}-{color.name.upper()}"
                            variant, variant_created = ProductVariant.objects.get_or_create(
                                product=product,
                                size=size,
                                color=color,
                                defaults={
                                    'sku': sku,
                                    'stock_quantity': 10,
                                    'price_adjustment': Decimal('0.00')
                                }
                            )
                            if variant_created:
                                variant_count += 1
                    
                    if variant_count > 0:
                        self.stdout.write(f'  Created {variant_count} variants for {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )
        self.stdout.write('You can now:')
        self.stdout.write('1. Run: python manage.py runserver')
        self.stdout.write('2. Visit: http://127.0.0.1:8000/')
        self.stdout.write('3. Admin: http://127.0.0.1:8000/admin/ (admin / admin123)')
