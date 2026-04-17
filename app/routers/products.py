from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import ProductCreate, ProductOut, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_all_products,
    get_product_by_product_id,
    update_product,
)

router = APIRouter(prefix="/products", tags=["Products"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    products = get_all_products(db)
    return templates.TemplateResponse("products.html", {"request": request, "products": products})


@router.get("/api", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return get_all_products(db)


@router.post("/api", response_model=ProductOut)
def add_product(data: ProductCreate, db: Session = Depends(get_db)):
    existing = get_product_by_product_id(db, data.product_id)
    if existing:
        raise HTTPException(status_code=400, detail="Product ID already exists")
    return create_product(db, **data.model_dump())


@router.put("/api/{product_id}", response_model=ProductOut)
def edit_product(product_id: str, data: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_by_product_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    return update_product(db, product, **update_data)


@router.delete("/api/{product_id}")
def remove_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_product_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    delete_product(db, product)
    return {"detail": "Product deleted"}
