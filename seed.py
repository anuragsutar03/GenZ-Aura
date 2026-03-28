from sqlalchemy.orm import Session
from models import Category, Product


def seed_data(db: Session):
    # Only seed if empty
    if db.query(Category).count() > 0:
        return

    # ── Categories (matching frontend category cards) ──
    categories_data = [
        {"name": "Hoodies", "label": "Bestseller", "emoji": "🧥", "item_count": 24},
        {"name": "Oversized Tees", "label": "New Drop", "emoji": "👕", "item_count": 36},
        {"name": "Cargo Pants", "label": "Trending", "emoji": "👖", "item_count": 18},
        {"name": "Accessories", "label": "Limited", "emoji": "🧢", "item_count": 12},
        {"name": "Co-ords", "label": "Hot", "emoji": "🔥", "item_count": 15},
        {"name": "Sale", "label": "Up to 50% Off", "emoji": "⚡", "item_count": 20},
    ]

    categories = []
    for c in categories_data:
        cat = Category(**c)
        db.add(cat)
        categories.append(cat)
    db.flush()

    # ── Products (matching the 8 product cards in the frontend) ──
    products_data = [
        {
            "name": "Acid Wash Oversized Hoodie",
            "category_id": categories[0].id,
            "price": 2499,
            "old_price": None,
            "badge": "new",
            "sizes": ["S", "M", "L", "XL"],
            "stock": 40,
            "gradient_class": "p1",
            "emoji": "🧥",
        },
        {
            "name": "Chrome Script Tee",
            "category_id": categories[1].id,
            "price": 1299,
            "old_price": None,
            "badge": "hot",
            "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
            "stock": 60,
            "gradient_class": "p2",
            "emoji": "👕",
        },
        {
            "name": "Void Cargo Pants",
            "category_id": categories[2].id,
            "price": 3299,
            "old_price": None,
            "badge": "new",
            "sizes": ["S", "M", "L", "XL"],
            "stock": 30,
            "gradient_class": "p3",
            "emoji": "👖",
        },
        {
            "name": "Glitch Relaxed Hoodie",
            "category_id": categories[0].id,
            "price": 1999,
            "old_price": 2799,
            "badge": "sale",
            "sizes": ["S", "M", "L"],
            "stock": 20,
            "gradient_class": "p4",
            "emoji": "🧥",
        },
        {
            "name": "Aura Drop Tee",
            "category_id": categories[1].id,
            "price": 999,
            "old_price": None,
            "badge": "ltd",
            "sizes": ["S", "M", "L", "XL"],
            "stock": 15,
            "gradient_class": "p5",
            "emoji": "👕",
        },
        {
            "name": "Neon Babe Co-ord Set",
            "category_id": categories[4].id,
            "price": 3799,
            "old_price": None,
            "badge": "new",
            "sizes": ["XS", "S", "M", "L"],
            "stock": 25,
            "gradient_class": "p6",
            "emoji": "🔥",
        },
        {
            "name": "Flame Graphic Tee",
            "category_id": categories[1].id,
            "price": 1499,
            "old_price": 1999,
            "badge": "sale",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "stock": 50,
            "gradient_class": "p7",
            "emoji": "👕",
        },
        {
            "name": "Cyber Bucket Hat",
            "category_id": categories[3].id,
            "price": 799,
            "old_price": None,
            "badge": "hot",
            "sizes": ["One Size"],
            "stock": 35,
            "gradient_class": "p8",
            "emoji": "🧢",
        },
    ]

    for p in products_data:
        product = Product(**p)
        db.add(product)

    db.commit()
    print("✅ GenZ Aura seed data loaded successfully!")
