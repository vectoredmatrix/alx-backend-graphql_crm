import os
import django
from decimal import Decimal
from django.utils import timezone
import random

# -------------------- SETUP DJANGO --------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order


# -------------------- SEED CUSTOMERS --------------------
def seed_customers():
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol White", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Green", "email": "david@example.com", "phone": "321-654-0987"},
        {"name": "Eve Black", "email": "eve@example.com", "phone": "+1478523690"},
    ]

    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data["email"], defaults=data
        )
        customers.append(customer)
    print(f"✅ Seeded {len(customers)} customers.")
    return customers


# -------------------- SEED PRODUCTS --------------------
def seed_products():
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Smartphone", "price": Decimal("699.99"), "stock": 25},
        {"name": "Tablet", "price": Decimal("399.99"), "stock": 15},
        {"name": "Headphones", "price": Decimal("149.99"), "stock": 40},
        {"name": "Smartwatch", "price": Decimal("249.99"), "stock": 20},
    ]

    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data["name"], defaults=data
        )
        products.append(product)
    print(f"✅ Seeded {len(products)} products.")
    return products


# -------------------- SEED ORDERS --------------------
def seed_orders(customers, products):
    orders = []
    for i in range(5):
        customer = random.choice(customers)
        selected_products = random.sample(products, k=random.randint(1, 3))
        total = sum([p.price for p in selected_products])
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            order_date=timezone.now()
        )
        order.products.set(selected_products)
        orders.append(order)
    print(f"✅ Seeded {len(orders)} orders.")
    return orders


# -------------------- MAIN FUNCTION --------------------
def run_seed():
    print("🌱 Seeding database...")
    customers = seed_customers()
    products = seed_products()
    seed_orders(customers, products)
    print("🌿 Database seeding complete!")


if __name__ == "__main__":
    run_seed()
