from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductImage, Color, Size, ProductVariant
from django.core.files import File
from django.conf import settings
from decimal import Decimal
import os
import random
import uuid

class Command(BaseCommand):
    help = 'Load fake product data with the specified image'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating fake data...'))
        
        # Path to the source image in static/images
        source_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'IMG-20260408-WA0033.jpg')
        
        if not os.path.exists(source_image_path):
            self.stdout.write(self.style.ERROR(f'Source image not found at {source_image_path}'))
            return

        # Ensure media/products directory exists
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        media_categories_dir = os.path.join(settings.MEDIA_ROOT, 'categories')
        os.makedirs(media_products_dir, exist_ok=True)
        os.makedirs(media_categories_dir, exist_ok=True)

        # 1. Create Fake Categories
        category_names = ['Men', 'Women', 'Kids', 'New Arrivals', 'Best Sellers']
        categories = []
        for name in category_names:
            slug = name.lower().replace(' ', '-')
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': f'Premium {name} collection'}
            )
            
            # Set category image if not set
            if not category.image:
                with open(source_image_path, 'rb') as f:
                    category.image.save(f'cat_{slug}.jpg', File(f), save=True)
            
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')

        # 2. Ensure some colors and sizes exist
        colors = []
        for c_name, c_hex in [('Black', '#000000'), ('White', '#FFFFFF'), ('Grey', '#808080')]:
            color, _ = Color.objects.get_or_create(name=c_name, defaults={'hex_code': c_hex})
            colors.append(color)

        sizes = []
        for s_name in ['S', 'M', 'L', 'XL']:
            size, _ = Size.objects.get_or_create(name=s_name)
            sizes.append(size)

        # 3. Create Fake Products
        product_prefixes = ['Comfort', 'Classic', 'Premium', 'Essential', 'Luxury']
        product_suffixes = ['Briefs', 'Boxers', 'Trunks', 'Tee', 'V-Neck']

        for i in range(10):
            name = f"{random.choice(product_prefixes)} {random.choice(product_suffixes)} {i+1}"
            slug = f"fake-product-{uuid.uuid4().hex[:8]}"
            category = random.choice(categories)
            price = Decimal(random.randint(200, 800))

            product = Product.objects.create(
                name=name,
                slug=slug,
                category=category,
                description=f"This is a high-quality {name} from our latest collection. Designed for ultimate comfort and durability.",
                short_description=f"High-quality {name}",
                base_price=price,
                stock_quantity=random.randint(10, 100),
                is_featured=random.choice([True, False]),
                is_active=True
            )
            
            product.available_sizes.set(sizes)
            product.available_colors.set(colors)
            
            # 4. Add the product image
            with open(source_image_path, 'rb') as f:
                product_image = ProductImage.objects.create(
                    product=product,
                    alt_text=name,
                    is_main=True,
                    order=0
                )
                product_image.image.save(f'prod_{slug}.jpg', File(f), save=True)

            # 5. Create Variants
            for size in sizes:
                for color in colors:
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        color=color,
                        sku=f"{slug.upper()}-{size.name}-{color.name[:3].upper()}",
                        stock_quantity=random.randint(5, 20),
                        price_adjustment=Decimal('0.00')
                    )

            self.stdout.write(f'Created product: {name}')

        self.stdout.write(self.style.SUCCESS('Successfully generated fake products and categories!'))
