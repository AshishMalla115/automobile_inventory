from django.core.management.base import BaseCommand
from inventory.models import Category, SparePart

class Command(BaseCommand):
    help = 'Loads sample categories and products into the database'

    def handle(self, *args, **kwargs):
        # Sample categories
        categories = [
            {
                'name': 'Engine Parts',
                'description': 'Essential engine components and accessories'
            },
            {
                'name': 'Brake System',
                'description': 'Brake pads, rotors, and related components'
            },
            {
                'name': 'Suspension',
                'description': 'Shocks, struts, and suspension components'
            },
            {
                'name': 'Electrical',
                'description': 'Batteries, alternators, and electrical components'
            },
            {
                'name': 'Body Parts',
                'description': 'Exterior and interior body components'
            }
        ]

        # Sample products
        products = [
            {
                'name': 'Oil Filter',
                'category': 'Engine Parts',
                'price': 15.99,
                'stock': 50,
                'description': 'High-quality oil filter for all vehicle types'
            },
            {
                'name': 'Brake Pads',
                'category': 'Brake System',
                'price': 45.99,
                'stock': 30,
                'description': 'Premium brake pads for optimal stopping power'
            },
            {
                'name': 'Shock Absorbers',
                'category': 'Suspension',
                'price': 89.99,
                'stock': 20,
                'description': 'Heavy-duty shock absorbers for smooth ride'
            },
            {
                'name': 'Car Battery',
                'category': 'Electrical',
                'price': 129.99,
                'stock': 15,
                'description': 'Long-lasting car battery with 3-year warranty'
            },
            {
                'name': 'Headlight Assembly',
                'category': 'Body Parts',
                'price': 199.99,
                'stock': 10,
                'description': 'Complete headlight assembly with LED technology'
            }
        ]

        # Create categories
        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            self.stdout.write(f'Created category: {category_data["name"]}')

        # Create products
        for product_data in products:
            category = Category.objects.get(name=product_data['category'])
            SparePart.objects.get_or_create(
                name=product_data['name'],
                category=category,
                defaults={
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'description': product_data['description']
                }
            )
            self.stdout.write(f'Created product: {product_data["name"]}')

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data')) 