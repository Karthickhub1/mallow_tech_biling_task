from pydantic import BaseModel, EmailStr


class ProductCreate(BaseModel):
    name: str
    product_id: str
    available_stocks: int
    price: float
    tax_percentage: float


class ProductUpdate(BaseModel):
    name: str | None = None
    available_stocks: int | None = None
    price: float | None = None
    tax_percentage: float | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    product_id: str
    available_stocks: int
    price: float
    tax_percentage: float

    class Config:
        from_attributes = True


class BillItem(BaseModel):
    product_id: str
    quantity: int


class BillRequest(BaseModel):
    customer_email: EmailStr
    items: list[BillItem]
    denominations: dict[int, int] = {}  # {500: count, 100: count, ...}
    cash_paid: float
