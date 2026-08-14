import os
import sys
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base import Base
from app.db.models import User, UserRole, Category, Product, ProductStatus, Inventory, Order, OrderItem, OrderStatus, Payment, PaymentStatus
from app.core.security import hash_password

CATEGORIES = [
    "Laptops & Computers", "Smartphones & Tablets", "Audio & Headphones", "Cameras & Photography",
    "Wearable Technology", "Gaming Consoles & Accessories", "TV & Home Theater", "Smart Home Devices",
    "Monitors & Displays", "Networking & Routers", "Storage & Hard Drives", "Computer Components",
    "Printers & Scanners", "Office Electronics", "Car Electronics", "Drones & Tech Toys",
    "Power Banks & Chargers", "Cables & Adapters", "Software & Subscriptions", "Refurbished Tech"
]

BRANDS = [
    "Apple", "Samsung", "Dell", "HP", "Lenovo", "Asus", "Acer", "Sony", "Bose", "Sennheiser",
    "Logitech", "Razer", "Corsair", "Nvidia", "AMD", "Intel", "LG", "Panasonic", "Canon", "Nikon",
    "DJI", "GoPro", "Anker", "TP-Link", "Netgear", "Western Digital", "Seagate", "Kingston", "Crucial", "MSI",
    "Gigabyte", "Sonos", "JBL", "Marshall", "Garmin", "Fitbit", "Microsoft", "Google", "OnePlus", "Xiaomi",
    "Huawei", "Realme", "Motorola", "Amazon", "Roku", "Belkin", "SanDisk", "EVGA", "Thermaltake", "Zotac"
]

PRODUCT_ADJECTIVES = ["Pro", "Ultra", "Max", "Lite", "Elite", "Gaming", "Wireless", "Smart", "Compact", "Portable"]
PRODUCT_TYPES = ["Notebook", "Phone", "Earbuds", "Speaker", "Monitor", "Keyboard", "Mouse", "Router", "SSD", "Camera"]

def seed_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("Seeding database...")

    # 1. Seed Roles/Users
    if db.query(User).count() == 0:
        admin_user = User(
            email="admin@ecommerce.com",
            full_name="System Admin",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN
        )
        inv_manager = User(
            email="inventory@ecommerce.com",
            full_name="Inventory Manager",
            hashed_password=hash_password("inv123"),
            role=UserRole.INVENTORY_MANAGER
        )
        db.add_all([admin_user, inv_manager])

        # Seed 100 Customer Users
        customer_users = []
        for i in range(1, 101):
            user = User(
                email=f"customer{i}@example.com",
                full_name=f"Customer User {i}",
                hashed_password=hash_password("user123"),
                role=UserRole.CUSTOMER
            )
            customer_users.append(user)
        db.add_all(customer_users)
        db.commit()
        print("Seeded 102 Users (1 Admin, 1 Inventory Manager, 100 Customers).")

    # 2. Seed Categories
    if db.query(Category).count() == 0:
        category_objects = []
        for cat_name in CATEGORIES:
            slug = cat_name.lower().replace(" ", "-").replace("&", "and")
            cat = Category(name=cat_name, slug=slug, description=f"Top quality products in {cat_name}")
            category_objects.append(cat)
        db.add_all(category_objects)
        db.commit()
        print(f"Seeded {len(category_objects)} Categories.")

    categories = db.query(Category).all()

    # 3. Seed Products & Inventory (1000+ products)
    existing_products = db.query(Product).count()
    if existing_products < 1000:
        needed = 1000 - existing_products
        print(f"Generating {needed} products with inventory...")

        products_to_add = []
        for i in range(1, needed + 1):
            brand = random.choice(BRANDS)
            adj = random.choice(PRODUCT_ADJECTIVES)
            ptype = random.choice(PRODUCT_TYPES)
            cat = random.choice(categories)
            sku = f"SKU-{brand[:3].upper()}-{i:04d}-{random.randint(100,999)}"
            name = f"{brand} {adj} {ptype} {i}"
            price = round(random.uniform(19.99, 1999.99), 2)
            rating = round(random.uniform(3.5, 5.0), 1)

            prod = Product(
                sku=sku,
                name=name,
                description=f"High performance {name} with premium features designed by {brand}.",
                category_id=cat.id,
                brand=brand,
                price=price,
                currency="USD",
                rating=rating,
                status=ProductStatus.ACTIVE,
                version=1
            )
            products_to_add.append(prod)

        db.add_all(products_to_add)
        db.flush()

        # Add corresponding Inventory records
        inventory_to_add = []
        for prod in products_to_add:
            stock = random.randint(10, 500)
            inv = Inventory(
                product_id=prod.id,
                stock_quantity=stock,
                reserved_quantity=0,
                version=1
            )
            inventory_to_add.append(inv)

        db.add_all(inventory_to_add)
        db.commit()
        print(f"Successfully seeded {len(products_to_add)} Products with Inventory records.")

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
