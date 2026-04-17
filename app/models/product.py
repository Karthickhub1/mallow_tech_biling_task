from sqlalchemy import Column, Float, Integer, String

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    available_stocks = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False, default=0.0)
