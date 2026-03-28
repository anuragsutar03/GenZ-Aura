from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, engine, Base
from models import Product, Category, CartItem, NewsletterSubscriber, Order, OrderItem
from schemas import (
    ProductOut, ProductCreate,
    CategoryOut, CategoryCreate,
    CartItemCreate, CartItemOut, CartSummary,
    NewsletterSubscribe, NewsletterOut,
    OrderCreate, OrderOut,
    AddToCartRequest,
)
import seed

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GenZ Aura API",
    description="Backend for the GenZ Aura streetwear e-commerce platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod: replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed on startup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed.seed_data(db)


# ── PRODUCTS ─────────────────────────────────────────────

@app.get("/products", response_model=List[ProductOut], tags=["Products"])
def get_products(
    category_id: Optional[int] = None,
    badge: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get all products. Filter by category or badge (new/hot/sale/ltd)."""
    q = db.query(Product)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if badge:
        q = q.filter(Product.badge == badge)
    return q.limit(limit).all()


@app.get("/products/{product_id}", response_model=ProductOut, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductOut, tags=["Products"])
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ── CATEGORIES ───────────────────────────────────────────

@app.get("/categories", response_model=List[CategoryOut], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    """Get all product categories."""
    return db.query(Category).all()


@app.get("/categories/{category_id}", response_model=CategoryOut, tags=["Categories"])
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category with its products."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@app.post("/categories", response_model=CategoryOut, tags=["Categories"])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    cat = Category(**data.dict())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ── CART ─────────────────────────────────────────────────

@app.get("/cart/{session_id}", response_model=CartSummary, tags=["Cart"])
def get_cart(session_id: str, db: Session = Depends(get_db)):
    """Get all cart items for a session. Use any unique string as session_id."""
    items = db.query(CartItem).filter(CartItem.session_id == session_id).all()
    total = sum(i.product.price * i.quantity for i in items)
    item_count = sum(i.quantity for i in items)
    return CartSummary(items=items, total=round(total, 2), item_count=item_count)


@app.post("/cart/{session_id}/add", response_model=CartItemOut, tags=["Cart"])
def add_to_cart(session_id: str, data: AddToCartRequest, db: Session = Depends(get_db)):
    """Add a product to the cart. If already in cart, increments quantity."""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing = db.query(CartItem).filter(
        CartItem.session_id == session_id,
        CartItem.product_id == data.product_id,
        CartItem.size == data.size,
    ).first()

    if existing:
        existing.quantity += data.quantity
        db.commit()
        db.refresh(existing)
        return existing

    item = CartItem(
        session_id=session_id,
        product_id=data.product_id,
        size=data.size,
        quantity=data.quantity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/cart/{session_id}/item/{item_id}", tags=["Cart"])
def remove_from_cart(session_id: str, item_id: int, db: Session = Depends(get_db)):
    """Remove a specific item from the cart."""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.session_id == session_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


@app.delete("/cart/{session_id}", tags=["Cart"])
def clear_cart(session_id: str, db: Session = Depends(get_db)):
    """Clear all items from a cart session."""
    db.query(CartItem).filter(CartItem.session_id == session_id).delete()
    db.commit()
    return {"message": "Cart cleared"}


# ── ORDERS ───────────────────────────────────────────────

@app.post("/orders", response_model=OrderOut, tags=["Orders"])
def place_order(data: OrderCreate, db: Session = Depends(get_db)):
    """Place an order from the current cart session."""
    items = db.query(CartItem).filter(CartItem.session_id == data.session_id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    order_items = []
    for item in items:
        product = item.product
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}",
            )
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append(OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            size=item.size,
            price_at_purchase=product.price,
        ))
        product.stock -= item.quantity

    order = Order(
        session_id=data.session_id,
        name=data.name,
        email=data.email,
        address=data.address,
        city=data.city,
        pincode=data.pincode,
        total=round(total, 2),
        items=order_items,
    )
    db.add(order)

    # Clear cart after order
    db.query(CartItem).filter(CartItem.session_id == data.session_id).delete()
    db.commit()
    db.refresh(order)
    return order


@app.get("/orders/{order_id}", response_model=OrderOut, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Track an order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ── NEWSLETTER ───────────────────────────────────────────

@app.post("/newsletter/subscribe", response_model=NewsletterOut, tags=["Newsletter"])
def subscribe(data: NewsletterSubscribe, db: Session = Depends(get_db)):
    """Subscribe to the GenZ Aura newsletter."""
    existing = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == data.email
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already subscribed")
    sub = NewsletterSubscriber(name=data.name, email=data.email)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@app.get("/newsletter/subscribers", response_model=List[NewsletterOut], tags=["Newsletter"])
def get_subscribers(db: Session = Depends(get_db)):
    """Get all newsletter subscribers (admin use)."""
    return db.query(NewsletterSubscriber).all()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
