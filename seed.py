"""Seed the database with sample products and default denominations."""

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models.denomination import Denomination
from app.models.product import Product

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Seed products
sample_products = [
    {"name": "Notebook", "product_id": "P001", "available_stocks": 100, "price": 250.00, "tax_percentage": 12.0},
    {"name": "Pen", "product_id": "P002", "available_stocks": 500, "price": 20.00, "tax_percentage": 5.0},
    {"name": "Eraser", "product_id": "P003", "available_stocks": 300, "price": 10.00, "tax_percentage": 5.0},
    {"name": "Pencil Box", "product_id": "P004", "available_stocks": 50, "price": 150.00, "tax_percentage": 18.0},
    {"name": "Geometry Set", "product_id": "P005", "available_stocks": 80, "price": 350.00, "tax_percentage": 12.0},
    {"name": "Backpack", "product_id": "P006", "available_stocks": 40, "price": 800.00, "tax_percentage": 18.0},
]

for prod_data in sample_products:
    existing = db.query(Product).filter(Product.product_id == prod_data["product_id"]).first()
    if not existing:
        db.add(Product(**prod_data))
        print(f"  Added product: {prod_data['name']} ({prod_data['product_id']})")
    else:
        print(f"  Product already exists: {prod_data['product_id']}")

# Seed denominations
for value in settings.DENOMINATIONS:
    existing = db.query(Denomination).filter(Denomination.value == value).first()
    if not existing:
        db.add(Denomination(value=value, count=100))  # Start with 100 of each denomination
        print(f"  Added denomination: {value} (count: 100)")
    else:
        print(f"  Denomination already exists: {value}")

db.commit()
db.close()
print("\nSeeding complete!")
