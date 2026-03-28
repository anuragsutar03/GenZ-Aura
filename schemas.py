from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ── CATEGORY ─────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    label: Optional[str] = None
    emoji: Optional[str] = None
    item_count: Optional[int] = 0


class CategoryOut(BaseModel):
    id: int
    name: str
    label: Optional[str]
    emoji: Optional[str]
    item_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── PRODUCT ──────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    category_id: int
    price: float
    old_price: Optional[float] = None
    badge: Optional[str] = None
    sizes: Optional[List[str]] = ["S", "M", "L", "XL"]
    stock: Optional[int] = 50
    gradient_class: Optional[str] = None
    emoji: Optional[str] = "👕"


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int
    price: float
    old_price: Optional[float]
    badge: Optional[str]
    sizes: List[str]
    stock: int
    gradient_class: Optional[str]
    emoji: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── CART ─────────────────────────────────────────────────

class AddToCartRequest(BaseModel):
    product_id: int
    size: str
    quantity: int = 1


class CartItemCreate(BaseModel):
    product_id: int
    size: str
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    session_id: str
    product_id: int
    size: str
    quantity: int
    product: ProductOut
    added_at: datetime

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: List[CartItemOut]
    total: float
    item_count: int


# ── ORDER ─────────────────────────────────────────────────

class OrderCreate(BaseModel):
    session_id: str
    name: str
    email: EmailStr
    address: str
    city: str
    pincode: str


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    size: str
    price_at_purchase: float
    product: ProductOut

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    session_id: str
    name: str
    email: str
    address: str
    city: str
    pincode: str
    total: float
    status: str
    items: List[OrderItemOut]
    created_at: datetime

    class Config:
        from_attributes = True


# ── NEWSLETTER ────────────────────────────────────────────

class NewsletterSubscribe(BaseModel):
    name: str
    email: EmailStr


class NewsletterOut(BaseModel):
    id: int
    name: str
    email: str
    subscribed_at: datetime

    class Config:
        from_attributes = True
