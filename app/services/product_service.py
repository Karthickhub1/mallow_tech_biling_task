from sqlalchemy.orm import Session

from app.models.product import Product


def get_all_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product_by_product_id(db: Session, product_id: str) -> Product | None:
    return db.query(Product).filter(Product.product_id == product_id).first()


def create_product(db: Session, name: str, product_id: str, available_stocks: int, price: float, tax_percentage: float) -> Product:
    product = Product(
        name=name,
        product_id=product_id,
        available_stocks=available_stocks,
        price=price,
        tax_percentage=tax_percentage,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, **kwargs) -> Product:
    for key, value in kwargs.items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
