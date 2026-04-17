import math

from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.services.denomination_service import (
    calculate_balance_denominations,
    update_denomination_counts,
)


def generate_bill(
    db: Session,
    customer_email: str,
    items: list[dict],  # [{"product_id": str, "quantity": int}]
    denominations_received: dict[int, int],  # {500: 2, 100: 1, ...}
    cash_paid: float,
) -> dict:
    """
    Generate a bill: validate products, calculate totals, create invoice,
    update stock and denominations, compute balance change.
    """
    invoice_items = []
    total_without_tax = 0.0
    total_tax = 0.0

    # Validate and build line items
    for item in items:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        if not product:
            raise ValueError(f"Product '{item['product_id']}' not found")
        if product.available_stocks < item["quantity"]:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.available_stocks}, Requested: {item['quantity']}"
            )

        purchase_price = product.price * item["quantity"]
        tax_amount = purchase_price * (product.tax_percentage / 100)
        total_price = purchase_price + tax_amount

        total_without_tax += purchase_price
        total_tax += tax_amount

        invoice_items.append(
            InvoiceItem(
                product_id=product.product_id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item["quantity"],
                purchase_price=round(purchase_price, 2),
                tax_percentage=product.tax_percentage,
                tax_amount=round(tax_amount, 2),
                total_price=round(total_price, 2),
            )
        )

    net_price = total_without_tax + total_tax
    rounded_net_price = math.ceil(net_price)  # Round up to nearest integer
    balance = cash_paid - rounded_net_price

    if balance < 0:
        raise ValueError(
            f"Insufficient payment. Bill total: {rounded_net_price}, Paid: {cash_paid}"
        )

    # Create invoice
    invoice = Invoice(
        customer_email=customer_email,
        total_without_tax=round(total_without_tax, 2),
        total_tax=round(total_tax, 2),
        net_price=round(net_price, 2),
        rounded_net_price=rounded_net_price,
        cash_paid=cash_paid,
        balance=balance,
    )
    invoice.items = invoice_items
    db.add(invoice)

    # Deduct stock
    for item in items:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        product.available_stocks -= item["quantity"]

    # Update shop denominations with received cash
    update_denomination_counts(db, denominations_received)

    # Calculate balance denominations to return
    balance_denoms = calculate_balance_denominations(db, int(balance))

    db.commit()
    db.refresh(invoice)

    return {
        "invoice": invoice,
        "balance_denominations": balance_denoms,
    }


def get_invoices_by_email(db: Session, email: str) -> list[Invoice]:
    return (
        db.query(Invoice)
        .filter(Invoice.customer_email == email)
        .order_by(Invoice.created_at.desc())
        .all()
    )


def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()
