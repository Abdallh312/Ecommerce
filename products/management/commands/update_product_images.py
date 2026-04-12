from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from django.core.files import File
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Update all products to use the specified image as their main image'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating product images...'))
        
        # Path to the source image in static/images
        source_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'IMG-20260408-WA0033.jpg')
        
        if not os.path.exists(source_image_path):
            self.stdout.write(self.style.ERROR(f'Source image not found at {source_image_path}'))
            return

        # Ensure media/products directory exists
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_products_dir, exist_ok=True)

        products = Product.objects.all()
        count = 0

        for product in products:
            # Update or create main product image
            main_image = product.images.filter(is_main=True).first()
            
            if not main_image:
                main_image = ProductImage(product=product, is_main=True, order=0)
            
            with open(source_image_path, 'rb') as f:
                filename = f'prod_{product.slug}.jpg'
                main_image.image.save(filename, File(f), save=True)
            
            count += 1
            self.stdout.write(f'Updated image for product: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated images for {count} products!'))
